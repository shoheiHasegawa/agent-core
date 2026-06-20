# Life Automation Project Roadmap

## Phase 4: COO Module E2E & Orchestration [Completed]
- **実績**: `DailyPlanningService` を呼び出す `cli.py` と、タスクをファイルから読み書きする `MarkdownTaskRepository` を実装。
- **インフラ**: Google Calendar API の Desktop App (OAuth2) フロー対応と、E2Eテスト環境の構築。
- **アーキテクチャ**: SOLID/DDD/TDDの観点でサブエージェントによるレビューを実施。ユースケースのフロー制御を `orchestrator.py` に分離し、タスクIDの同一性（Identity）を担保する `MarkdownTaskParser` を導入するなど、堅牢なアーキテクチャへのリファクタリングを完遂。

## Phase 5: Inbox Triage Prototype & COO Refactoring [Completed]
**目標**: 今後の完全なAgent駆動体制に向けた基盤整理と、Agentによるトリアージのプロトタイプ作成を行う。

### 1. COO モジュールの技術的負債返済 (Refactoring)
- **実績**: `presentation/cli.py` を廃止し、`entry_point.py` と `factory.py` の構成に統一。フェイルファストとExit Codeのハンドリングを実装。
- **実績**: サブエージェント（Architect/Reviewer）による自動レビューとDIP（依存性逆転）の適用。

### 2. Inbox Triage と双方向パイプラインの構築
- **実績**: Agent自身が `00_Drop_Zone` を読み込み、タスクに Life Portfolio カテゴリと UUID を付与して整形する `.agent/skills/inbox-triage/SKILL.md` を作成。
- **アーキテクチャ**: `00_Inbox` 配下を「データの流れる順」にプレフィックス付きの窓口（00〜03）に再編し、人間とAIが非同期にタスクを依頼し合う「Agent OS Inbox Pipeline」を定義。

## Phase 6: Agent Architecture Revamp & Focus-Driven Planning [Future]
**目標**: Personaを廃止し「Workflow, Skill, Gate」のパイプラインへAgentアーキテクチャを再編する。そして、役職ごとの上位目標（Focus）に基づくスケジューリングと、Agentによる非同期タスク処理を実現する。

### 1. Agent アーキテクチャと `.agent` ディレクトリの再構築
- `life-automation` と `second-brain` の `.agent` ディレクトリの責務を分離し、自律開発向けとパーソナルアシスタント向けに再構築する。
- 曖昧な「Persona（人格）」レイヤーを廃止し、「Constitution（憲法/ルール）」「Skill（能力）」「Workflow（手順）」「Gate（DoR/DoD等）」の明確な構造へ再設計する。
- Areas配下と `.agent` 配下の境界を明確に定義し、「How（システムルール）」は `.agent` に、「What/Why（生き方の目標）」は `20_Areas` に集約する。

### 2. 既存実装への Life Portfolio カテゴリ反映
- `Task` ドメインエンティティに `category` プロパティを追加し、パーサーを修正する。
- `DailyPlanningService` が Google Calendar に予定を登録する際、カテゴリ（Work/Growth等）に応じてカレンダーの色を変更する機能をインフラ層に実装する。


### 3. Focus-Driven Planning の実装
- `second-brain/02_Areas/Life_Management/` 配下に CEO, PM, CFO, COO の役職ごとの目標（Focus）を定義する。
- 毎朝のWorkflowでAgentが「現在のFocus」を読み込み、余白(Buffer)を確保した上で1日のスケジュールを組む仕組みを構築する。

## Phase 7: Inbox Pipeline Operation & Review Workflow の実装 [Future]
**目標**: Worker Agent の自律稼働と、「計画・実行」の後の「振り返り・改善（PDCA）」ループを確立する。

### 1. Agent OS Inbox Pipeline の本格稼働
- Worker Agent が `01_Agent_Queue` を監視し、バックグラウンドで自律的にタスクを消化して `02_Review_Queue` へ報告する仕組み（定期実行またはイベント駆動）を構築する。
- CIO Agent が週末に `03_Idea_Backlog` を読み込み、`20_Areas` 等のZettelkastenへナレッジを昇華させるフローを構築する。

### 2. Daily Review
- 1日の終わりにAgentが「今日のFocusは達成できたか？」「確保した余白時間でどんな新しい気づきがあったか？」をヒアリングし、Episodic Log に残す。

### 3. Weekly Review (Life Portfolio 予実分析と改善)
- 週末に CFO / PM Agent が完了したタスクのカテゴリと見積もり時間（`est`）を集計し、「Life Portfolio 投資比率レポート」を生成する（Check）。
- 分析結果を元に、次週のFocus（投資配分）を調整し、不足している領域（休息など）の余白を強制確保するフィードバックループを確立する（Action）。

### 4. Someday / Idea の退避先 (Backlog) 管理
- トリアージで弾いたタスク（今日/今週やらないもの）やアイデアを管理・再浮上させる仕組みを整備する。
