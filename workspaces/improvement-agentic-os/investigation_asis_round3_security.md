# As-Is Security & Data Isolation Audit Report (Round 3)

## 概要
`you_inc/agent-core/` の As-Is 状態における、Agentのデータ汚染・機密漏洩リスク（Leave No Trace原則の破綻）について監査を実施した結果、**MUSTレベルの深刻なセキュリティ・データ隔離債務が4点**検出されました。

現在の設計は、意図せずローカル環境に機密データを永続化させたり、Gitリポジトリにクレデンシャルや顧客データを混入させる脆弱性を抱えています。

---

## 検出された深刻な脆弱性 (MUST-Level Debts)

### 1. `scratch/` ディレクトリに対する「Leave No Trace」原則の検証漏れによるデータ永続化
* **発生箇所**: `tools/verify_cleanliness.py` (L64付近) および `workspaces/*/scratch/`
* **問題点**: 
  ドキュメント (`workspace_management.md`) 上では、「`scratch/` の中のファイルはフェーズ完了時に破棄すること」と定義されています。しかし、品質ゲートとして機能する `verify_cleanliness.py` では `exclude_dirs = {..., "scratch", ...}` として**`scratch/` 内のチェックを完全に除外**しています。
* **セキュリティリスク**:
  Agentが一時的なエラーログ、機密データを含むAPIレスポンスのダンプ、または中間処理用のファイルを `scratch/` に作成した場合、自律的な削除が行われない限りローカルディスク上に永続化されます（Git管理外のため、開発者も気づきにくい）。これにより、エージェント間やセッション間でコンテキストが漏洩・汚染される重大なリスクがあります。

### 2. `session-manager` の盲目的な `git add .` による `.env` (クレデンシャル) 流出リスク
* **発生箇所**: `Makefile` (L14-16) および `skills/session-manager/SKILL.md` (L37)
* **問題点**:
  `Makefile` には sops を利用した `secrets-decrypt` コマンドが存在し、実行するとカレントディレクトリに `.env` が生成（復号）されます。しかし、**`.gitignore` では `config/secret.env` などは除外されていますが、ルートの `.env` が除外されていません**。
  さらに、`session-manager` の Handoff（セッション終了）手続きでは、確認なしに `git add . && git commit ... && git push` が実行されます。
* **セキュリティリスク**:
  開発中やデバッグ時に一度でも `make secrets-decrypt` を実行した状態でセッションが Handoff を迎えると、機密情報が含まれた `.env` がリモートリポジトリにそのまま Push され、重大なクレデンシャル流出を引き起こします。

### 3. Workspaces 内の機密データのGit永続化
* **発生箇所**: `workspaces/<Epic名>/` および `skills/session-manager/SKILL.md`
* **問題点**:
  `workspaces/` ディレクトリは「実行現場 (The Core SSOT)」として定義されており、タスクの進捗 (`tasks/progress.md`) やコンテキスト (`tasks/context.md`) が記録されます。
  しかし、これらがそのまま Git 管理下に置かれているため、Agentが処理した**ユーザーのプライベートな情報、生データ、機密性の高い要件**などが一時的にこれらに記載された場合、`session-manager` の `git add .` によってGitの履歴に不可逆的に記録・Pushされてしまいます。
* **セキュリティリスク**:
  「作業場」と「ソースコードリポジトリ」の境界が曖昧なため、データ隔離（Data Isolation）が成立していません。

### 4. Handoff ログの意図的な追跡によるコンテキスト漏洩
* **発生箇所**: `.gitignore` (L10: `!events/handoff_*.md`)
* **問題点**:
  `.gitignore` にて、`events/` 配下のファイルは基本的に除外されていますが、`!events/handoff_*.md` によって Handoff のログファイルだけが意図的に Git の追跡対象にされています。
* **セキュリティリスク**:
  Handoff ログには直近のセッションでの会話内容や、AIが処理したコンテキストの要約が含まれる可能性があります。ランタイムの実行ログ（ユーザーとの対話に関する文脈）がソースコードと共にリポジトリに保存されるのは、データアイソレーションの観点から不適切です。

---

## 修正への推奨アクション (Next Steps)

1. **強制的な `scratch/` のパージ**:
   * Handoff 時（またはセッション開始時）に、全ワークスペースの `scratch/` ディレクトリ内を物理的に `rm -rf` するステップを `pre_handoff_verify.sh` や `session-manager` に組み込む。
2. **`.gitignore` の見直し**:
   * ルートディレクトリの `.env` を直ちに `.gitignore` に追加する。
   * `events/handoff_*.md` を追跡対象から外す（ローカルの履歴としてのみ保持するか、DB等に移行する）。
3. **`git add .` の廃止と選択的コミットの導入**:
   * `session-manager` における `git add .` を止め、`agent-core/docs/` や `agent-core/skills/` など、**追跡すべき設定・ドキュメントディレクトリのみを選択的に `git add`** するセーフリスト（Allowlist）方式に変更する。
   * `workspaces/` 内の機密データが含まれうる領域のGit管理方針を見直す。
