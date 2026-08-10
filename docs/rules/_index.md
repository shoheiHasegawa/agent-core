# Execution Constraints Index (実行制約インデックス)

本ディレクトリ（`agent-core/docs/rules/`）には、Agentがタスクを実行する際に遵守すべき具体的な「制約（Execution Constraints）」が配置されている。
**⚠️ 指示（Agent向け）**: 自身のタスクに必要な制約のみを以下のリストから検索・抽出し、JITロード（読み込み）すること。不要なルールを読み込むとコンテキスト汚染の原因となるため厳禁である。

## ルール一覧

- `dialog_heuristics.md`: ユーザーとの対話・壁打ちやプロファイリング（ジョハリの窓など）を行う際の制約。
- `orchestration.md`: Tier 1 (Orchestrator) エージェントがジョブやワーカーを組み立てる際の制約。ハードコードの禁止など。
- `sdd_tdd_heuristics.md`: 仕様書（spec.md）の作成や、TDDにおけるテスト作成の制約。
- `system_heuristics.md`: システムやアーキテクチャの運用に関する制約。
- `tool_design_principles.md`: 新しいツールやコマンド（JSON-First Protocol準拠）を実装する際の制約。
- `zettelkasten_heuristics.md`: Zettelkastenノート（Inbox, Sense-Making, Permanent）の作成や蒸留に関する制約。
