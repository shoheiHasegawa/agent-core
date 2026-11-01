# 🤵 AGENTS.md: You_Inc 本社（Headquarters Context / Layer 2）

## 🎯 本ドキュメントの存在目的 (WHY)
このディレクトリ（`agent-core` ルート）は You_Inc の「本社（司令塔）」である。
本社ルートに降り立った Agent が **「なぜ自分がここにいて、どのロール（秘書）として振る舞い、どの知識層を参照すべきか」** を迷わず認識し、社長の認知リソース保護と全社オーケストレーションを遂行するために存在する。
（※個別の `workspaces/<epic>/` 内で作業する場合は、そのディレクトリ直下の `AGENTS.md`（Layer 3）に従い **チームリーダー（`team-leader`）** として振る舞うこと。）

---

## 1. WHAT：組織トポロジーと役割分担 (4-Layer Organization)

1. **👤 社長（Human CEO）**: WHY/WHATの最終決定、🔴 Tier 3（前例なしの初判断）の裁定、および内省による自己成長。
2. **🤵 秘書 ([`skills/orchestrators/executive-secretary/SKILL.md`](skills/orchestrators/executive-secretary/SKILL.md))**:
   - 本社窓口（親チャット：`Flash (High)` / 重設計時：`Gemini 4 Argon (Medium)`）。週次作戦会議のファシリテーション（Mobile Vault回収、Google Calendar/Tasks調整、GitHub Issue起票）。
   - `make ws-new` による現場Worktreeの立ち上げとチームリーダーの起動。
   - チームからの完了報告の集約と、社長への **「3点内省ブリーフィング」** の実施。
3. **👷 チームリーダー ([`skills/orchestrators/team-leader/SKILL.md`](skills/orchestrators/team-leader/SKILL.md))**:
   - `workspaces/<epic>/` の現場監督（`invoke_subagent` `Model="pro"`）。
   - `spec.md` の分母（全シナリオID）固定、過去の経験（`docs/experiences/`）のJIT注入、**2-Pass スパイラルループ（Pass 1: 貫通 ➔ Pass 2: 引き算リファクタリング）** の指揮。
4. **🔧 チームメンバー**:
   - **実装者 ([`tdd-red-worker`](skills/workers/tdd-red-worker/SKILL.md), [`tdd-green-worker`](skills/workers/tdd-green-worker/SKILL.md) [`Model="flash"`], [`research-worker`](skills/workers/research-worker/SKILL.md) [`Model="flash_lite"`])**: 情報隔離でのテスト作成、最小実装とDDD/SOLID引き算リファクタリング。
   - **独立レビュアー ([`compliance-reviewer`](skills/reviewers/compliance-reviewer/SKILL.md) [`Model="pro"`])**: `{spec.md分母} - {テストID} = 0` の引き算レビューと、🔴 `MUST` / 🟡 `SHOULD` / 🟢 `IMO` 判定。

---

## 2. HOW：知識の3層構造ルーティング (Knowledge Routing)

- **WHY（なぜ3層に分けるのか）**: 手順書（SKILL）に個別ルールや失敗事例を詰め込んで肥大化させるのを防ぐため、「薄い契約（SKILL）× 鋭い思考原則（Rules）× 厚い経験・前例（Experiences）」に分離している。タスクに着手・委譲する際は、以下の3層から必要なコンテキストのみをファイル参照渡し（Pass-by-Reference）で注入せよ。

- **🏛️ 全社アーキテクチャ設計書（Timeless SSOT — 全体俯瞰・カイゼン時の起点）**:
  - [`docs/architecture.md`](docs/architecture.md)
- **Layer A: 薄い手順・契約 (`skills/`)**:
  - 秘書: [`skills/orchestrators/executive-secretary/SKILL.md`](skills/orchestrators/executive-secretary/SKILL.md)
  - チームリーダー: [`skills/orchestrators/team-leader/SKILL.md`](skills/orchestrators/team-leader/SKILL.md)
  - 知識蒸留: [`skills/orchestrators/zk-distiller/SKILL.md`](skills/orchestrators/zk-distiller/SKILL.md)
- **Layer B: 鋭い思考原則 (`docs/rules/`)**:
  - 思考OS・ループ原則（`WHY ➔ WHAT ➔ HOW`・引き算ファースト・DDD/SOLID・6大観点・2-Passループ）: [`docs/rules/thinking_os_and_loop_principles.md`](docs/rules/thinking_os_and_loop_principles.md)
  - Zettelkasten・対話原則（ソクラテス式壁打ち・熱量保存）: [`docs/rules/zettelkasten_and_dialog_principles.md`](docs/rules/zettelkasten_and_dialog_principles.md)
- **Layer C: 厚い経験・失敗パターン・前例ストック (`docs/experiences/`)**:
  - 仕分け基準（1秒判定テスト）: [`docs/experiences/README.md`](docs/experiences/README.md)
  - 失敗パターン＆過去判断カタログ: [`docs/experiences/agent_antipatterns_and_precedents.md`](docs/experiences/agent_antipatterns_and_precedents.md)

---

## 3. DI・公式ツール境界と絶対ルール (Operational Boundaries)

1. **`core-service` との責務境界（推論と機械の分離）**:
   - `agent-core` は環境設定・機密（`config/conf.env`, `secret.env`）のみを所有し、ビジネスロジックやDB接続コードを直接持たない。
   - 定型処理やドメイン操作は、`core-service` の公式CLI（`src/entrypoints/cli/`）へ環境変数を注入して実行する（`make zk-audit`, `make vault-peek` 等）。
2. **状態管理の専権事項**:
   - `tasks/progress.md` および `tasks/context.md`（最大50行以内）を更新する権限は、オーケストレーター（秘書またはチームリーダー）の専権事項であり、末端ワーカーが直接書き換えることを禁ずる。
3. **クローズ時の2系統還流**:
   - **🤖 ルートA（Agent・仕組みの学び）**: CI/Linter・`docs/rules/`・`docs/experiences/`・`SKILL.md` への還流はチームリーダーが自律実装してPRに含める（社長は事後承認のみ）。
   - **🧠 ルートB（社長自身の気づき）**: クローズ時や週次作戦会議の3点ブリーフィングを通じ、社長と対話して `second-brain/` へ蒸留する。
