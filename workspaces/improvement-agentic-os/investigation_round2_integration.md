# Agentic OS 移行リスク評価レポート: Thin Orchestrator + PubSub Queue

## 1. 概要
現在の「Fat Orchestration（Daisy Chain型）」から「Thin Orchestrator + Blackboard Queue（PubSub）」への非同期モデル移行に伴う、MUSTレベルの破壊リスクと隠れた依存関係の調査結果。

## 2. MUSTレベルの移行リスク（既存プロセスが完全に破壊されるポイント）

### A. 状態管理（State Management）の競合破壊（Race Conditions）
- **隠れた依存関係**: 現在のシステム（`session-manager`等）は、`tasks/progress.md` や `tasks/context.md` という単一のMarkdownファイルを「同期的な状態ストア」として扱い、Agent自身が直接更新している。
- **破壊リスク**: PubSub化により複数のサブエージェント（Worker）が非同期・並行に稼働し始めると、Markdownファイルへの同時書き込み（Race Condition）が発生し、ファイル破損や先祖返り（Lost Update）が確実におきる。
- **対策必須要件**: Markdownによる直接の自己トラッキングを廃止し、排他制御可能なデータベース（SQLite `you_inc_ops.db`）や、単一のState Manager専用Agent（Blackboard管理者）に書き込み操作を一本化するアーキテクチャ変更が不可欠。

### B. オーケストレーターの「インメモリ・コンテキスト」依存による健忘（Amnesia）
- **隠れた依存関係**: 現在の `sdd-loop-orchestrator` 等は、サブエージェントを `invoke_subagent` で同期的に呼び出し、**「待機中のLLMのコンテキストウィンドウ（メモリ）」にワークフローの中間状態（これまで何をしたか、次は何をするか）を保持**している。
- **破壊リスク**: PubSub経由でタスクをPublishしてOrchestratorが待機状態（Suspend）に入りコンテキストが解放されると、Workerが完了してキューに結果（Subscribe）が返ってきた際、Orchestratorは「自分が何をしていたか」を忘却しており、継続処理がフォールトする。
- **対策必須要件**: Orchestratorをステートレスに保つため、タスクの相関ID（Correlation ID）と、現在のフローの進捗ステートマシン（State Machine）を外部（DBやBlackboard上）で永続化・復元する仕組み（Context Hydration）が不可欠。

### C. 同期的な Exit Criteria（完了条件）と Handoff の崩壊
- **隠れた依存関係**: `AGENT.md` のQuality Gateや `session-manager` の「Handoffプロトコル」は、「すべての作業が順次終わり、最後に一括で `make check-all` や `pre_handoff_verify.sh` を同期実行する」ことを前提としている。
- **破壊リスク**: PubSubで完全非同期化されると、「いつすべてのタスクが完了したか（Global Done）」の判定が極めて困難になる。検証スクリプトが中途半端な状態で走り、永続的にエラーを出してHandoff（セッション終了）ができなくなるデッドロックが発生する。
- **対策必須要件**: Blackboard上に「Epic / Task の依存関係グラフ（DAG）」を持たせ、すべてのサブタスクが `COMPLETED` になったイベントをトリガーとして、初めて CI/Handoff ワーカーを起動する「イベント駆動型の品質ゲート」への再設計が必要。

### D. エラーハンドリングとロールバックの迷子
- **隠れた依存関係**: 現在、エラーが発生した場合は同期的ループの中でAgentがそのまま回復処理（Plan Bの提示など）を行っている。
- **破壊リスク**: PubSubキュー上でWorkerがクラッシュした場合、非同期ゆえにOrchestratorにエラーが直接返らない可能性がある。現在の `agent-core/events/` だけでは、特定のエラーがどのワークフローに属するものか紐付けられず（Context Loss）、リカバリーが放置されてシステムがハングする。
- **対策必須要件**: DLQ（Dead Letter Queue）の導入と、すべてのメッセージに対するOrigin（親タスクID）の付与。エラーイベントをフックして回復処理をアサインする専用の「Supervisor / Exception Handler」の設置。

## 3. 結論
PubSub/Blackboardモデルへの移行は、単なる「呼び出し方の変更」ではなく、**「LLMのコンテキストウィンドウへの状態依存からの脱却」と「ファイルベースの排他制御の撤廃」**というアーキテクチャの根幹を覆す変更です。
特に `progress.md` への書き込み競合と、Orchestratorの記憶喪失（ステートマシン不在）は、移行直後にシステム全体を機能不全に陥らせる「MUSTレベルのブロッカー」となります。これらのステート管理の改修を、非同期キューの導入よりも先行して（あるいは同時に）行う必要があります。
