# 💡 AgentOS Expansion Idea: CCO Morning Insight (Morning Discovery)

## 概要
当初「AgentOS Upgrade」プロジェクトの Phase 4 として予定していた CCO (Chief Creativity Officer) による「モーニング・インサイト」の自律実装案。
現時点では具体的な入力ソースやアルゴリズムの仕様が未確定のため、一旦プロジェクトスコープから外し、将来的な拡張アイデアとして保存する。

## 実装上の未決定事項（検討材料）

### 1. 外部情報のソース (Input Source)
- **RSS/Arxiv**: 具体的にどのカテゴリやURLをターゲットにするか。
- **Focus Topics**: ユーザーの現在の関心をどうやってエージェントに伝えるか（`Focus_Topics.md` 等の運用）。

### 2. RAG / 知的衝突のロジック
- **類似度検索の戦略**: 既存の Permanent Note (180本以上) から、どうやって「意味のある対立や補完」を見つけ出すか。
- **CCO Personality**: 「素晴らしい」と褒めるのではなく、既存知識の前提を疑わせる「ソクラテス的な問い」をどう生成するか。

### 3. デリバリー形式
- 毎朝 `launchd` で起動し、`01_Inbox` へ Markdown 形式でインサイトを配信するパイプライン。

## 関連プロジェクト
- [[Project Overview: AgentOS Upgrade]]
- [[05_Task_Backlog]]

## 次のアクション
- 関心が再燃したタイミングで、具体的な RSS フィードリストを作成し、プロトタイプ実装を開始する。
