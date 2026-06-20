# Phase01: second-brain 初期実装タスク

## 1. 目標
社長（人間）とAgentが共に育てる企業内図書館として、プログラムの実行状態を含まず純粋な情報・知識のみを永続化するスケルトンを構築する。

## 2. ディレクトリ構造の作成
以下のフラットなネットワーク構造を初期作成する。
- `00_Inbox/` (一次フォーマット待機キュー)
- `10_Areas/` (会社のルール・戦略・指針)
- `20_Sense_Making/` (蒸留待ちインキュベーション領域)
- `30_Resources/` (外部資料・参照元)
- `40_Permanent_Notes/` (普遍的な知識・教訓)
- `90_Meta/System_Rules/` (システム制約・マニュアル)
- `90_Meta/Templates/` (各種Markdownテンプレート)
- `90_Meta/Attachments/` (孤立ファイル用)

## 3. 必須ファイルの作成
### 3.1. ルートファイル
- `README.md` (目的と全体像)
- `GEMINI.md` (絶対ルールとJITロードポインタ)
- `INDEX.md` (詳細ディレクトリマップ)
- `CONTRIBUTING.md` または `RULES.md` (各フォルダの役割・タグ命名規則)

### 3.2. テンプレートとYAMLスキーマ (`90_Meta/Templates/` 配下)
以下7種のテンプレートを作成し、共通の必須YAMLスキーマ（type, status, created, updated, tags, requires_human）を組み込む。
1. `Area_Governance_Template.md`
2. `Permanent_Note_Template.md`
3. `Resource_Template.md`
4. `Inbox_Raw_Template.md`
5. `Agent_Task_Request_Template.md`
6. `Project_Charter_Template.md`
7. `Dashboard_Briefing_Template.md`

## 4. 基盤コード・仕組みの実装要件
- **コミット前品質ゲートの構築**: CI（Push後）ではなく、ローカルの `pre-commit` フックや Obsidian プラグイン等を利用して、AgentによるDirect Commitの前に「MarkdownのYAMLフォーマット妥当性」や「内部リンク切れ」を検知し、未然に防ぐ仕組みを構築する。
- **JITロードの実現**: `GEMINI.md` からのポインタを活用し、タスクごとに必要なビジネス制約（`10_Areas/`）やシステム制約（`90_Meta/System_Rules/`）のみを遅延ロードさせるルーティングの設計。
