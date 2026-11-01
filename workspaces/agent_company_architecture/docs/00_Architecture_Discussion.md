# You_Inc「Agentが働く会社」アーキテクチャ設計書 (SSOT)

本ドキュメントは、You_Inc を「社長（人間） ⇄ 秘書 ⇄ チームリーダー ⇄ チームメンバー」の組織として稼働させるための設計議論（WHY ➔ WHAT ➔ HOW）を記録する正本（SSOT）である。

---

## 0. アジャイル設計の基本姿勢（何を今固め、何を後から育てるか）

| 分類 | 対象（WHY / WHAT の骨格 vs HOW の肉付け） | ステータス |
| :--- | :--- | :--- |
| **🏛️ 最初に固めた骨格**<br>（後から変えると負債になるもの） | 1. **組織の4層構造・命名・モデル配分ルール**<br>2. **自律ループの5大定義・2周スパイラル・「分母引き算」の検証構造**<br>3. **データの置き場所（SoRの境界）と2大窓口（PC=Antigravity / スマホ=Gemini）**<br>4. **ブランチ戦略と回収フロー**（Worktree + PR回収）<br>5. **`agent-core` と `core-service` の責務・DI・公式CLI境界** | **本ドキュメント（1〜4章）にて完全合意済み** |
| **🌱 小さく始めて育てる実装**<br>（MVP Step 1〜4） | 1. `main` の未コミット整理と Worktree ハーネス（`make ws-new` / `ws-harvest`）の構築<br>2. 既存19スキルの退避と、4大フロー逆算の新コアSKILL・3階層文書の作成<br>3. `core-service` の DI自己完結化・公式CLI移管（脱 `app_context.py`）<br>4. 新体制（秘書 ➔ チームリーダー ➔ Worktree ➔ PR回収）での初陣試運転 | **Step 1 から順次実装** |

---

## 1. WHY（目的と基本思想）— 【確定】

1. **社長の認知リソース保護と「ブラックボックス化」の防止**:
   - 社長は「WHY/WHATの最終決定」と「初めての未決事項の判断」に専念する。
   - ただし、Agent任せにして社内構造がブラックボックス化（裸の王様化）したり社長自身の成長が止まるのを防ぐため、クローズ時に必ず**「①何をなぜ変えたか、②Agentが何を学びどう仕組み化したか、③社長自身の気づき（Second Brain候補）への問い」の3点ブリーフィング**を行い、自分を通して咀嚼・内省化する。
2. **コンテキスト純度の維持**:
   - **秘書**、**チームリーダー**、**メンバー（実装者・独立レビュアー）** に階層を分け、ファイル参照渡し（Pass-by-Reference）でコンテキストの劣化・圧迫を防ぐ。
3. **「SKILLは薄く、思考原則は鋭く、経験（学び）は厚く」**:
   - **① SKILL (`skills/`)**: 入出力の契約と停止条件のみを薄く定義する（頻繁に変えない）。
   - **② 思考のOS (`docs/rules/` コア原則)**: DDD・SOLID・YAGNIおよび**「引き算ファースト（足し算バイアスの抑制）」**という抽象度の高い思考プロセスをインストールし、個別ルールの無限膨張を防ぐ。
   - **③ 経験・失敗パターン集 (`docs/experiences/` 等)**: 現場で起きた具体的な失敗パターンや過去の社長判断（前例）は別の場所に厚くストックし、チームリーダーがタスクに応じて必要なものだけをピンポイントでJIT注入する。
4. **「AIの思考（`agent-core`）」と「安定した機械（`core-service`）」の分離**:
   - 静的にチェックできるもの（Linter/CI）や定型業務ツールはAgentの推論に委ねず、すべてスクリプト・CLI化する。
   - 業務・公式CLIツールはすべて `core-service` に集約して公開し、`agent-core` は外から環境変数を注入してその口をキックするだけの極薄の司令塔とする。

---

## 2. WHAT（確定した5大アーキテクチャ骨格）— 【確定】

### 骨格1：4層組織・「前例ベース」3段階介入トリアージ・モデル配分
* **組織階層**:
  * **👤 社長（あなた）**: 意思決定・最終承認・内省による自己成長。
  * **🤵 秘書 (`executive-secretary`)**: 社長の唯一の本社窓口。スケジュール/ToDo調整、GitHub Issue起票、Worktree起動、報告・内省ブリーフィング。
  * **👷 チームリーダー (`team-leader`)**: Epic/Issue単位の現場監督。`spec.md` の分母定義、過去の経験・前例の選定注入、2周スパイラルループの進行管理。
  * **🔧 チームメンバー**:
    - **実装メンバー (`tdd-red-worker`, `tdd-green-worker`, `research-worker`)**: テスト作成、実装とDDDリファクタリング、`make check-all` の通過。
    - **独立レビュアー (`compliance-reviewer`)**: 実装者と分離された検査役。
* **人間が介入する頻度を減らす「前例（Precedent）ベースの3段階判断トリアージ」**:
  * **🟢 Tier 1：前例あり・ルール明確 ➔ 【自律決定 ＆ 事後承認】**: 過去の判断基準や前例から導けるものは人間を止めずにリーダーが自律決定し、完了時に「過去の〇〇の判断に基づきAを採用」と事後報告する。
  * **🟡 Tier 2：前例の応用・軽微な選択 ➔ 【根拠付き推奨案で1タップ承認】**: 白紙で質問せず、「過去の〇〇の原則から【案A（推奨）】が整合的です。案Aで進めてよいですか？」と秘書経由で提案する。
  * **🔴 Tier 3：初めての判断（前例なし）・不可逆な決定 ➔ 【事前エスカレーション】**: 前例のないWHY/WHATの分岐のみ作業を止めて社長へ上げる。**一度社長が判断した結果は必ず経験ストックへ記録し、次回からは自動的に 🟢 Tier 1（事後承認）へ降格させる（自律性の複利向上）**。
* **モデル配分（Argon温存・コスト最適化）**:
  * 社長との重い設計壁打ちのみ `Argon (Medium)` または `Flash (High)`。
  * チームリーダーは **`Flash (High)`**、メンバー・レビュアーは **`Flash (Medium / Low)`** を明示指定して高速回転させる。

---

### 骨格2：自律ループの5大定義項目と「2-Pass スパイラル × SDD/TDD ダブルループ」
LLMレビュアー特有の「無限に細かい指摘をひねり出して過品質になる問題」と、Outside-In TDD特有の「とりあえずテストだけ通してDDDが崩壊する問題」を、以下の構造で同時に解決する。

#### (1) 外側と内側の責務分離（Outside-In SDD × TDD ダブルループ）
* **🌐 外側のループ（Integration Test / 契約の固定）**:
  - `spec.md` の全シナリオID（6大観点：正常系・異常系・境界値・冪等性・外部同期・不変条件）と1対1で対応し、モック禁止で公開Serviceの入出力契約をロックする。
* **🔬 内側のループ（Unit Test ＋ 必須DDDリファクタリング）**:
  - Domain層（Entity / ValueObject）の境界値・エッジケースを網羅する。
  - **「引き算ファースト」とDDD保護**: `tdd-green-worker` はテストが通っただけでは完了とせず、**「UseCaseからビジネスロジックをDomainモデルへ抽出し、不要な冗長コードを削る（Delete ➔ Simplify ➔ Add）」リファクタリング**を完了条件に必須化する。

#### (2) 後続工程への波及影響（Downstream Impact）を軸にした指摘レベル分類
* 🔴 **`MUST`（Blocker / 即修正必須）**:
  - **放置すると後続工程の別Agentが誤解・手戻りを起こすもの（特に上流の `spec.md` における曖昧な表現・記述ミス・シナリオ漏れは、見た目が小さくても後続TDDを狂わせるため無条件で `MUST`）**。
  - `make check-all` の失敗、契約未達、または重大なアーキテクチャ境界（DIP/SRP）違反。
* 🟡 **`SHOULD`（Non-Blocker / Pass 2 で一括洗練）**:
  - 契約と動作は満たし後続も狂わせないが、1周動かしてみた結果見えた構造改善（Domainへのさらなる責務抽出、重複統合、命名改善）。1周目では差し戻さずリスト化し、2周目でまとめて解消する。
* 🟢 **`IMO`（Opinion / 今やらない・YAGNI）**:
  - 今回の分母スコープ外の将来拡張案や好みの問題。過品質を防ぐため今回のループでは修正禁止とし、必要ならBacklog/経験ストックへメモするのみ。

#### (3) 段階的に品質を高める「2-Pass スパイラルループ」と5大定義項目
1. **Pass 1（1周目：貫通 — Make it Work）**: 小バッチ（1〜2シナリオずつ）で全シナリオを一通りGreenにし、まず全体を通して動かす（🔴 `MUST` のみ解消、🟡 `SHOULD` は記録して保留）。
2. **Pass 2（2周目：全体俯瞰と引き算 — Make it Right）**: 1周して全体が動いた状態（テスト防波堤が100%ある状態）で全体を俯瞰し、溜まった 🟡 `SHOULD` と責務の歪みを「引き算のリファクタリング」で一括洗練させて完了する。
3. **定量的・決定論的な完了条件（Exit Criteria）**:
   - `make check-all` 終了コード `== 0`（Cov $\ge 90\%$、SDD差分 `0`） **かつ** 独立レビュアーの 🔴 `MUST` 指摘 `== 0件`。
4. **定量的・決定論的な異常停止条件（Circuit Breaker）**:
   - **同一エラー連続失敗 `== 2回`**、**1バッチ往復上限 `== 3周`**、または **🔴 Tier 3（前例なしの仕様矛盾）の発生** のいずれかで即座に強制停止し、`tasks/context.md` に原因仮説とA/B選択肢を書いてエスカレーションする。

---

### 骨格3：Workspaceブランチ戦略（方式A）と3リポジトリ独立CI
* **方式Aの物理構造**:
  * 本社（`agent-core` ルート）は常に `main` ブランチに保ち、`workspaces/` 配下を `.gitignore` する。
  * `make ws-new EPIC=<name>` 実行時、`workspaces/<name>/` に `agent-core` の Worktree（ブランチ `epic/<name>`）を切り、さらに必要な対象リポジトリ（`core-service` 等）を `workspaces/<name>/worktrees/<repo>/` に Worktree マウントする。
* **クローズ時のPR回収**: Epic完了時、`make ws-harvest` で作業用一時ファイルを掃除し、「昇格したルール・経験ストック・SKILL改善」のみを残して 각リポジトリの `main` へ PR を出す（途中経過もPRのコミット履歴に完全保存される）。
* **3リポジトリ独立CI**: `core-service`, `agent-core`, `second-brain` それぞれが他リポジトリへの相対パス依存を持たず、単体で `make check-all` と GitHub Actions CI を完結させる。

---

### 骨格4：2系統の学習還流フローと SKILL ゼロベース再構築
* **クローズ時の2系統の学習還流**:
  1. **🤖 ルートA（Agent・仕組みの学び）**: ① CI/Linter（静的チェック化）、② `docs/rules/`（思考原則）＆ `docs/experiences/`（失敗パターン・前例ストック）、④ `SKILL.md`（手順修正）への還流は、**チームリーダーが自律実装してPRに含め、社長は3点ブリーフィングを読んで事後承認（PRマージ）するのみ**。
  2. **🧠 ルートB（社長自身の気づき・哲学）**: ③ `second-brain/`（`20_Sense_Making` / `40_Permanent_Notes`）への還流は、**クローズ時の内省プロンプトや週次作戦会議を通じて秘書と社長が対話（壁打ち）して蒸留する**。
* **既存19スキルのアーカイブ退避とゼロベース再構築**:
  * 旧体制前提の既存19スキルは一旦退避し、4大業務フローから逆算した **最小コアSKILL（`executive-secretary`, `team-leader`, `tdd-red-worker`, `tdd-green-worker`, `compliance-reviewer`, `zk-distiller` 等）** を新規作成する（既存SKILLからは「情報隔離」「先回り実装禁止」「熱量維持」などの失敗の学びのみを抽出して移植する）。

---

### 骨格5：社長の「2大窓口（PC＝Antigravity / スマホ＝Gemini）」と個人タスク管理
* **💻 PC・デスク窓口 ＝ Antigravity（本社秘書）**:
  * 週1回（日曜など）の「週次作戦会議（15分）」で、`Mobile Vault` のメモ回収、来週の予定・期限タスクのセット、GitHub Issue 起票、および社長の内省蒸留を行う。
* **📱 スマホ・外出先窓口 ＝ Gemini アプリ ＆ iPhone ウィジェット**:
  * **予定・期限タスク・ルーティン**: **Google Calendar ＆ Google Tasks（ToDoリスト）** に統一（旧SQLiteタスク管理を代替）。iPhoneホーム画面のウィジェットで常時視認する。
  * **思考・アイデアの種**: **Obsidian (`Mobile Vault`)** にプレーンな `.md` として記録する。

---

## 3. HOWの詳細構造（文書階層・通信規約・DI/Tools境界）— 【確定】

### 3.1 `README.md` 一本化と 3階層 `GEMINI.md` / `AGENTS.md`
* 各リポジトリの全体地図・コマンド説明は **`README.md` 1枚に一本化**し、`INDEX.md` 等は廃止する。
* **自動階層ロードの配置**:
  1. **Layer 1 (`/you_inc/GEMINI.md`)**: 全社共通の憲法（シンボリックリンク解除、Rule 11 も旧スキル名依存を排し「変更時は影響範囲と引き算ファーストの代替案を提示せよ」へ更新）。
  2. **Layer 2 (`agent-core/AGENTS.md`)**: 本社を開いた時に秘書（`executive-secretary`）として自動認識させる起動スイッチ。
  3. **Layer 3 (`workspaces/<epic>/AGENTS.md`)**: 旧 `_index.md` を昇格。そのEpicの「Goal・DoD・対象Issue」を記載し、チームリーダーの常駐メモリとする。

### 3.2 「ファイル参照渡し（Pass-by-Reference）」通信規約
* リーダー ⇄ メンバー ⇄ レビュアー間で、チャット返り値に長いコードや指摘全文を直接書くことを禁ずる。
* 詳細はすべてファイル（`git diff`, `scratch/review_report.md`, `tasks/lessons_learned.md`）に出力し、チャットには **「ファイルパス ＋ 1〜3行の合否ステータス（MUST件数等）」のみ** を流す。

### 3.3 `agent-core` と `core-service` の DI・Tools 境界（公式CLIの集約）
* **業務・公式CLIの `core-service` 完全集約**:
  - 組み立て（`src/di/` の環境変数Bootstrap）と業務CLIの口（`src/entrypoints/cli/`：Zettelkasten操作、Mobile Vault操作等）はすべて **`core-service` 側** で持ち、公式コマンドとして公開する。
  - `validate_sdd.py`（`core-service` のSDD/DDD検証スクリプト）も `core-service/tools/` へ移管し、`core-service` 単体で `make check-all` が完結するようにする。
* **`agent-core` の極薄化（脱 `app_context.py`・脱業務Pythonコード）**:
  - `agent-core` は `config/`（`conf.env`, `secret.env`）と `Makefile`（Worktree操作および `uv run --project ../core-service --env-file config/conf.env ...` による公式CLIキック）と軽量なドキュメントLinterのみを持ち、`app_context.py` や旧SQLite管理スクリプト・ジョブ群はすべて廃止する。

---

## 4. アジャイル実装ロードマップ（MVP Step 1〜4）

| Step | フェーズ名 | 具体的な実装内容 | 完了条件（DoD） |
| :--- | :--- | :--- | :--- |
| **Step 1** | **Git整理 ＆ Worktree基盤構築**<br>（Bootstrap） | 1. 現在の `agent-core` / `core-service` の `main` 未コミット変更を整理・コミット<br>2. `validate_sdd.py` を `core-service` へ移管し単体 `make check-all` を自立化<br>3. `agent-core/Makefile` に `make ws-new` / `make ws-harvest` を実装し、`workspaces/` のWorktree運用を開始可能にする | `make ws-new` で `workspaces/<epic>/` 配下に `agent-core` と `core-service` のWorktreeが切れ、単体で `make check-all` が通ること |
| **Step 2** | **3階層文書 ＆ 新コアSKILL構築**<br>（Worktree試運転 #1） | 1. 3階層 `GEMINI.md` / `AGENTS.md` と `README.md` 一本化（`INDEX.md` 廃止）<br>2. 既存19スキルをアーカイブ退避し、失敗の学びを `docs/rules/` & `docs/experiences/` へ抽出<br>3. 新コアSKILL（`executive-secretary`, `team-leader`, `tdd-red/green-worker`, `compliance-reviewer`, `zk-distiller`）の作成とLinter更新 | 新設したWorktreeからPRを作成し、`agent-core` の `make check-all` がパスして `main` へマージされること |
| **Step 3** | **DI自己完結化 ＆ 公式CLI移管**<br>（Worktree試運転 #2） | 1. `core-service/src/di/` の環境変数Bootstrap化と `src/entrypoints/cli/` 新設<br>2. `agent-core/app_context.py` と旧SQLite用 `tools/`・`jobs/` の完全廃止<br>3. 3リポジトリへの最小 GitHub Actions CI（`.github/workflows/ci.yml`）の配置 | **秘書 ➔ チームリーダー（2-Passループ）** の新体制で実装・引き算レビュー・PR回収までを完走すること |
| **Step 4** | **本格稼働（週次作戦会議 ＆ 実務Issue）** | 1. 秘書と第1回の作戦会議を実施し、実務の GitHub Issue を起票して自律チームを稼働させる | 社長が「秘書との対話」と「3点ブリーフィングによる内省・承認」だけで会社を回せること |
