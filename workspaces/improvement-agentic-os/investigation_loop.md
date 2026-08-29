# Loop Engineering 調査レポート: オーケストレーションの肥大化とPubSubキューの欠如

## 1. 調査の背景と目的
`GEMINI.md`, `AGENT.md` および `agent-core/docs/` (特に `data_flow.md`, `skill_design_principles.md`, `development_standard.md`) を基に、現在の You_Inc Agentic OS のアーキテクチャを Loop Engineering（自律ループの設計）の観点から調査しました。

本レポートでは、現在の「Fat Orchestration（肥大化したオーケストレーション）」モデルから生じる MUST レベルの技術的負債と、「Thin Orchestration ＋ 非同期PubSub/掲示板」モデルへの移行の必要性について論じます。

## 2. 現行アーキテクチャの課題 (Fat Orchestration の限界)

現在の Agentic OS は「2-Tier Architecture」を採用し、Tier 1 (Orchestrator) が Tier 2 (Worker サブエージェント) を `invoke_subagent` 等で明示的に呼び出し、制御を管理する中央集権型の **Fat Orchestration** となっています。

### MUSTレベルの負債
1. **オーケストレーターのコンテキスト肥大化と認知負荷**
   - `sdd-loop-orchestrator` や `night-routine-orchestrator` などの司令塔は、フロー全体の状態遷移や各サブエージェントの呼び出し順序、エラー時のリトライロジックをすべて自身のプロンプト（コンテキスト）に抱え込んでいます。
   - 処理ステップが増えるほどオーケストレーターのコンテキストが肥大化し、LLMのハルシネーションリスク増大や、本来の「抽象的な意図の翻訳（WHYの解釈）」という責務への集中を妨げています。

2. **密結合による自律性の阻害と同期的な待機**
   - 司令塔がワーカーを直接呼び出す（Subagent Delegation）ため、司令塔はワーカーの処理完了を同期的に待つ必要があります。
   - これにより、Agent間の真の非同期並行処理が制限され、1つのワーカーがスタックするとフロー全体が停止する脆弱性（単一障害点）を抱えています。

## 3. 欠如している仕組み: PubSub的キューと Bulletin Board (掲示板)

`agent-core/events/` は「システムエラーの非同期通知」としては機能していますが（`data_flow.md` 参照）、**「Agent同士のタスク協調・状態共有」のための汎用的なメッセージキューや PubSub メカニズムが存在しません。**

### Thin Orchestration へのパラダイムシフト
オーケストレーターを「薄く（Thin）」保つためには、指示の伝達と状態管理を **Bulletin Board (掲示板) / Task Queue** に委譲する必要があります。

*   **PubSub メカニズムの導入**:
    *   司令塔（Orchestrator）は、ワーカーを直接呼び出すのではなく、タスク（例: `Test Creation Required`, `Implementation Required`）を非同期キューまたは掲示板に Publish して終了（または待機状態へ移行）します。
    *   各ワーカー（Tier 2）は、自身の専門スキルに関連するトピックを Subscribe しておき、タスクが出現した際に自律的にピックアップして実行します。
*   **イベント駆動のタスク進行**:
    *   実行完了や中間結果も掲示板に Publish され、必要に応じてレビューワーカー（`compliance-reviewer` 等）が自発的に検証を開始します。
    *   オーケストレーターは掲示板の状態（マイルストーンの達成度）を監視するだけで済み、個別の呼び出しロジックをコンテキストから排除できます。

## 4. 改善へのアクションプラン (Next Steps)

1. **Task Event Bus の新設**
   - 現在の `agent-core/events/` (エラー用) とは別に、Agent間のタスク依頼・結果通知を行う `agent-core/task_board/` または PubSubキューを構築する。
2. **Orchestrator の責務縮小 (Thin化)**
   - `sdd-loop-orchestrator` から個別のワーカー呼び出しコードを剥がし、「Epic/Specを分解して Task Queue に投入する」責務と、「Queue の完了状態を監視する」責務に特化させる。
3. **ワーカーの自律駆動化 (Event-Driven Workers)**
   - 各サブエージェントを Event-Driven に改修し、Queue に配置された特定フォーマットのタスク要求をトリガーとして自律起動する仕組みを実装する。

これにより、現在の密結合な呼び出しフローから脱却し、スケーラブルで耐障害性の高い完全な「自律型 Agentic OS」への進化が可能となります。
