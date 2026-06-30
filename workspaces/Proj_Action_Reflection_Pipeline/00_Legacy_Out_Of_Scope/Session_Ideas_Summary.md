# セッションアイデア棚卸し: Task and Calendar Automation

本セッション（および直近のアップデート）で議論・実装された主要なアーキテクチャ・アイデアの棚卸し記録です。

## 1. Agent OS Inbox Pipeline の構築
人間とAIエージェントが非同期かつ自律的に協働するための「データの流れ」を再定義しました。
- `00_Inbox` を段階的な窓口に再編（`00_Drop_Zone`, `01_Agent_Queue`, `02_Review_Queue`, `03_Idea_Backlog`）。
- 人間がラフなメモを Drop Zone に投げ込み、Agent がそれを解釈・トリアージして Queue や Backlog に振り分ける「双方向パイプライン」の思想。

## 2. Life Portfolio のシステムへの統合
単なるタスク管理から「人生のポートフォリオ管理」へ昇華させるための実装を行いました。
- タスクエンティティに `LifePortfolioCategory`（Work, Growth, Health, Social 等）を導入し、ファクトリ（`TaskFactory`）経由で生成。
- インフラ層に `ColorMapper` を導入し、Google Calendar 上の予定カラーをカテゴリごとに自動分類（可視化）する仕組み。

## 3. Focus-Driven Planning と Buffer (余白) の確保
詰め込み型のスケジュールから、意図と余裕を持ったスケジュールへの転換。
- `HolidayDetectionService` と `BufferGenerationPolicy` を導入し、休日判定や意図的な「余白時間」の確保をシステム化。
- 将来的には、`02_Areas/Life_Management/` に定義された各役職（CEO, PM, CFO, COO）のFocus（注力領域）を毎朝読み込み、それに基づいた投資配分で1日のスケジュールを組む仕組み（Phase 6）。

## 4. Agent アーキテクチャの刷新 (Persona から Pipeline へ)
自律型AIエージェントの振る舞いをより確実かつ透過的にするための設計方針。
- 曖昧になりがちな「Persona（人格）」レイヤーを廃止。
- 代わりに「Constitution（憲法/ルール）」「Skill（能力）」「Workflow（手順）」「Gate（DoR/DoD等）」という明確に定義されたパイプライン構造へと再設計。
- 責務の分離：「How（システムとしての処理手順）」は `.agent` に、「What/Why（生き方の目標や価値観）」はZettelkasten（`20_Areas`）に集約する。

---
*※ 本ドキュメントは `second-brain/10_Projects/Task_and_Calendar_Automation/` 直下に記録されています。ロードマップ (`Life_Automation_Roadmap.md`) も同ディレクトリに移動・統合済みです。*
