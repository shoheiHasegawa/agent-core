# Migration Strategy (移行計画)

## 1. 移行の背景と目的
旧アーキテクチャでは「実行層」と「知識層」が混在し、アーカイブの肥大化がAgentのコンテキスト汚染（ハルシネーションの要因）を招いていました。最新のADR（0005, 0006, 0008, 0009）に基づき、静的なナレッジベースである「second-brain」と動的な実行領域（agent-core等）を完全に分離し、Agent-Centricな純度の高いナレッジシステムへと移行します。

## 2. 移行工程

### Phase 1: 事前準備 (Pre-Migration)
- 【フェールセーフ】データロストや操作ミスに備え、現行システム全体（ASIS）の完全なバックアップ（GitのCommit/Tag打ち等）を取得する。
- 新規リポジトリ `second-brain` と実行層 `agent-core` の初期化とディレクトリ骨格の作成。
- Agentが処理するための統一YAMLタグ・メタデータのフォーマット定義の完了（Areasのテンプレート含む）。

### Phase 2: Parallel Build (並行稼働)
- 旧システムを読み取り専用（ReadOnly）に変更。
- 新規プロジェクトやタスクは `agent-core` のWorkspace/Epicとして開始する。
- 新しい知見の整理は `second-brain` 上の `Sense_Making` 経由で蓄積していく。

### Phase 3: データクレンジングと移行 (Data Cleansing & Migration)
既存データの棚卸しと、新構造へのマイグレーションを実施します。
※具体的なクレンジング手順は `02_data_cleansing_plan.md` を参照。
- **メタデータ変換とリンク修復**: ディレクトリ移動に伴う内部リンクの破損（Broken Links）の修復と、全ファイルへの新YAMLフロントマターの一括適用スクリプトを実行する。

### Phase 4: 旧リポジトリ廃止 (Decommission)
- 移行漏れがないかQuality Gateを設け、最終レビューを実施する。
- 【Validation】Lintツールやスクリプトを実行し、「リンク切れのゼロ確認」「必須メタデータの付与漏れ確認」を機械的に保証する。
- 孤立画像（Orphaned Attachments）などのクレンジングバッチを実行する。
- 旧ディレクトリを完全凍結（または消去）し、以降は `second-brain` のみを唯一の情報源とする。
