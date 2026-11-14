# Makefile 内包型 OS サンドボックス (Seatbelt) 自動強制仕様書

## 🎯 存在目的 (WHY)
プロンプト指示や開発者の注意力（性善説）に依存せず、`make check-all` や `make validate-tests`（および `make test`）を実行するだけで、macOS カーネル標準の `sandbox-exec`（Seatbelt）による OS レベルの物理保護（外部通信遮断・機密ファイルアクセス遮断・領域外書き込み遮断）を自動強制し、テスト時のセキュリティと決定論的再現性を担保するため。

---

## 📐 満たすべき状態と契約 (WHAT)

### 1. サンドボックス自動発動境界
- ホスト環境（非サンドボックス環境）から `make check-all`、`make validate-tests`、`make test`、および各静的検証ターゲット（`validate-skills`, `validate-orphans`, `validate-cleanliness`, `validate-links`）を実行した場合、注意力ゼロで自動的に `tools/sandbox_runner.py --role worker --worktree "$(CURDIR)" --` を経由して実行される。
- 実行時の `--worktree` 引数には常にカレント作業ディレクトリ（`$(CURDIR)`）が渡され、親リポジトリ直下での実行時も隔離 Worktree（`workspaces/<epic>/worktrees/agent-core`）内での実行時も、実行元の作業領域のみが書き込み許可される。
- **ホスト側 `check-all` の一括起動契約**: ホスト側の `check-all` は前提依存ターゲットを持たず、1回のみ `sandbox_runner.py --role worker --worktree "$(CURDIR)" -- $(MAKE) check-all` をキックする。これにより、各検証ターゲットごとの個別多重起動オーバーヘッドを完全に排除する。

### 2. 再入ガード (Re-entrancy Guard)
- macOS の `sandbox-exec` は多重起動（入れ子実行）を許容せず、`Operation not permitted` で失敗する。
- したがって、既にサンドボックス内部で動作している環境（環境変数 `YOU_INC_SANDBOX_ACTIVE=1` が設定されている状態）では、`Makefile` は `sandbox_runner.py` を再起動せず、直接テストコマンド・検証コマンドを実行する。
- `tools/sandbox_runner.py` は、サンドボックス配下でプロセスを起動する際、子プロセス環境に必ず `YOU_INC_SANDBOX_ACTIVE="1"` を注入する。

### 3. 公開インターフェースと環境変数契約
- **環境変数**: `YOU_INC_SANDBOX_ACTIVE`
  - 完全一致 `"1"` のみ: サンドボックス内部で稼働中（再入抑止フラグ）。
  - 未設定、空文字、`"0"`、その他文字列: ホスト環境（`sandbox_runner.py` 経由での自動起動が必要）。フェイルセーフ（Fail-closed）を死守する。
- **`tools/sandbox_runner.py` の契約拡張**:
  - `SANDBOX_ENV_VAR = "YOU_INC_SANDBOX_ACTIVE"` を定数定義。
  - `is_inside_sandbox() -> bool`: `os.environ.get(SANDBOX_ENV_VAR) == "1"` の完全一致でのみ `True` を返し、`"0"`・空文字・未設定・`"true"` 等では `False` を返す。
  - `run_in_sandbox(command, worktree_dir, scratch_dir=None, role="worker", allow_net=False, profile_path=DEFAULT_PROFILE, cwd=None, capture_output=False, env=None)`:
    - `env` 引数を許容し、指定がない場合は現在の `os.environ` をベースとして `YOU_INC_SANDBOX_ACTIVE="1"` を注入した辞書を子プロセスへ渡す。親プロセスの `os.environ` は書き換えない。
- **`Makefile` ターゲット契約**:
  - `.PHONY` に `test` を追加。
  - `test`: `validate-tests` のエイリアスとして定義。
  - `check-all`: サンドボックス内において全品質ゲートを同一順序で完走。
  - `validate-tests`: 単体テスト群を実行。
- **テストコードの配置と検証戦略**:
  - テストコードは `tests/test_makefile_seatbelt.py` に配置し、`make validate-tests`（`python -m unittest`）の対象とする。
  - **多重起動クラッシュ防止戦略**: テスト内部からの `make` 呼び出しは、GNU Make の dry-run モード（`make -n <target>`）の出力を検証する決定論的アサートを基本とし、サンドボックス内での多重 `sandbox-exec` 起動クラッシュを物理的に回避する。

---

## 🛠️ 実装方針 (HOW)

### 1. Makefile の構造
`Makefile` 内で `YOU_INC_SANDBOX_ACTIVE` が `"1"` か否かを厳密に評価し、サンドボックス内（`ifeq`）とサンドボックス外（`else`）でターゲット定義を分離する。
- **サンドボックス外 (`ifneq ($(YOU_INC_SANDBOX_ACTIVE),1)`)**:
  - `check-all`, `test`, `validate-tests`, `validate-skills`, `validate-orphans`, `validate-cleanliness`, `validate-links` を前提ターゲットなしで定義し、すべて `@uv run python tools/sandbox_runner.py --role worker --worktree "$(CURDIR)" -- $(MAKE) $@` として実行する。
- **サンドボックス内 (`ifeq ($(YOU_INC_SANDBOX_ACTIVE),1)`)**:
  - `validate-skills`, `validate-orphans`, `validate-cleanliness`, `validate-links`, `validate-tests` は直接 `uv run python tools/...` や `uv run python -m unittest ...` を実行する。
  - `check-all: validate-skills validate-orphans validate-cleanliness validate-links validate-tests` として定義し、各検証を順次実行して合格メッセージを出力する。
  - `test: validate-tests` として定義する。

### 2. `tools/sandbox_runner.py` の修正
- `SANDBOX_ENV_VAR = "YOU_INC_SANDBOX_ACTIVE"` を定義。
- `is_inside_sandbox() -> bool` を追加。
- `run_in_sandbox` に `env: dict[str, str] | None = None` を追加し、`run_env = (env if env is not None else os.environ).copy()` に `run_env[SANDBOX_ENV_VAR] = "1"` をセットして `subprocess.run(..., env=run_env)` を実行する。

---

## 🧪 検査シナリオ分母 (6大観点マトリクス)

### ① 正常系 (Happy Path)
- `[SC-SB-01]`: ホスト環境（`YOU_INC_SANDBOX_ACTIVE` 未設定）から `make -n validate-tests` を実行した際、出力に `sandbox_runner.py --role worker` が含まれ、自動的にサンドボックス経由で実行されるコマンド列が生成されること。
- `[SC-SB-02]`: サンドボックス内（`YOU_INC_SANDBOX_ACTIVE=1`）から `make -n check-all` および `make -n validate-tests` を実行した際、`sandbox_runner.py` が含まれず、直接対応するスクリプト・テストコマンド（`python -m unittest` 等）が生成されること（再入ガード）。

### ② 冪等性 (Idempotency)
- `[SC-SB-03]`: `make validate-tests` の dry-run および実行が複数回行われても、一時ファイルの残存や副作用が発生せず、常に同一の決定論的結果となること（Leave No Trace・冪等性）。

### ③ 境界値 (Boundary Conditions)
- `[SC-SB-04]`: ワークツリー境界および環境変数の境界値検証：
  - (a) カレントディレクトリ（`$(CURDIR)`）が `--worktree` 引数に正確に反映されること。
  - (b) `YOU_INC_SANDBOX_ACTIVE="0"`、空文字、未設定、`"true"`、`"2"` の場合、誤認されず確実にホスト側（`sandbox_runner.py` 経由）のコマンド列が生成されること（Fail-closed 境界値）。
  - (c) `sandbox_runner.is_inside_sandbox()` は環境変数が `"1"` の完全一致でのみ `True` を返し、`"0"`, `""`, None, `"true"` 等では `False` を返すこと。

### ④ 外部同期・調停 (Reconciliation)
- `[SC-SB-05]`: `tools/sandbox_runner.py` の `run_in_sandbox` は子プロセスの環境変数に `YOU_INC_SANDBOX_ACTIVE="1"` を注入し、親環境やホスト側の `os.environ` を破壊・残留させないこと（調停・透過伝播）。

### ⑤ 異常系・耐障害性 (Fault Tolerance)
- `[SC-SB-06]`: ホスト環境から `make -n check-all` を実行した際、前提ターゲット（`validate-skills` 等）を個別多重起動せず、1回のみ `sandbox_runner.py --role worker --worktree "$(CURDIR)" -- $(MAKE) check-all` を実行するコマンド列となること（多重起動防止・一括保護）。
- `[SC-SB-07]`: テスト実行コマンドが失敗した場合（exit code != 0）、`sandbox_runner.py` および `Makefile` がその失敗終了コードを正確に呼び出し元へ伝播すること。

### ⑥ ドメイン不変条件 (Domain Invariants)
- `[SC-SB-08]`: `Makefile` の `check-all` は、サンドボックス内において全品質ゲート（`validate-skills`, `validate-orphans`, `validate-cleanliness`, `validate-links`, `validate-tests`）を漏れなく同一順序で完走させること。
- `[SC-SB-09]`: 公開インターフェース `make test` が `validate-tests` のエイリアスとして定義され、ホスト環境（`sandbox_runner.py` 経由）およびサンドボックス内（直接実行）の双方で `validate-tests` と等価に動作すること（`.PHONY: test` 含む）。
