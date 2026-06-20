# ADR 0014: Mobile Integration Concept

## Context
日常の入力元（Input）であり、実行結果の閲覧先（Output）となる**モバイル環境（iPhone/iPad等）**と、コアアーキテクチャ（3層構造）の連携において、モバイル側に複雑なパースロジックを持たせると、保守性が著しく低下する課題があった。

## Decision
モバイル環境自体には複雑なパースロジックや自動化スクリプトを持たせず、**「純粋な入力の送信（Command）」**と**「コンパイル済データの閲覧（Read-Only View）」**の Thin Client として特化させる。

### A. 入力（Input / Command）
- **経路**: iOS Shortcuts / Obsidian Mobile 等 ➔ `second-brain/00_Inbox/`（iCloud同期等を経由）。
- **役割**: 思いつき、タスク、音声メモなどを、構造を気にせず「ただ投げ込む」だけ。
- **後続処理**: `agent-core` の `InboxTriageAgent` などがこれを拾い、正規化して適切な `second-brain` の奥深くに配置する。

### B. 出力・閲覧（Output / View）
- **経路**: `agent-core` が情報を要約・ビルド ➔ モバイルで閲覧。
- **解決策**: `second-brain` の複雑なPermanent Notes構造をそのまま探すのは認知負荷が高いため、`agent-core`（COOエージェント等）が、明日の予定や重要なタスクだけを抽出し、「モバイル専用の軽量なダッシュボード用Markdown（例: `Today.md`）」を生成・パブリッシュする。

## Consequences
- モバイルアプリ（Obsidian MobileやShortcuts）側の設定が極めてシンプルになり、API変更などの影響を受けにくくなる。
- Agentが要約したダッシュボードを見るだけになるため、モバイル操作時のUXが劇的に向上する。
