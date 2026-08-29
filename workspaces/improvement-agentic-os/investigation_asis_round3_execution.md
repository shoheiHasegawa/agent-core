# 調査報告: Tier 2 Agentのクラッシュとエラー伝播の断絶（Crash Recoveryの負債）

## 1. 背景とAs-Isの実行モデル (Background & As-Is Execution Model)
現在のAgentic OSにおいて、Orchestrator（Tier 1）は Worker（Tier 2）に対して非同期メッセージング（`invoke_subagent` や `send_message` ツール）を用いてタスクを委譲しています。タスクの委譲が完了すると、Orchestratorはシステムリソースを解放し、Workerからの「完了（または失敗）メッセージ」を待つリアクティブな待機状態（Suspended / Sleep）に移行します。

## 2. 課題: エラーの「闇への消失」現象 (The "Voiding" of Errors)
このアーキテクチャは正常系においては効率的ですが、異常系（Workerのクラッシュ時）において致命的な設計上の欠陥を露呈します。

1. **クラッシュの発生**: 
   Tier 2 Workerが、生成コードの構文エラー等による**未処理例外**、ハルシネーションによる**ツールの無限ループとイテレーション上限到達**、またはメモリ不足（OOM）などの**環境レベルのクラッシュ**に直面した場合、WorkerプロセスはOS（実行基盤）によって強制終了されます。
2. **伝播の断絶**: 
   強制終了されたWorkerは、死に際に Orchestrator へエラーを報告するための `send_message` を実行することができません。
3. **Orchestratorのゾンビ化 (Silent Hang)**: 
   現在、基盤側には Worker のプロセス死を検知して Orchestrator に代理でエラー通知（AgentCrashed イベントなど）を送る「スーパーバイザ層」が存在しません。結果として、エラーは文字通り「闇に消え」、Orchestrator は決して来ないメッセージを永遠に待ち続けるゾンビ状態（サイレントなデッドロック）に陥ります。

## 3. As-IsにおけるCrash Recoveryの欠如 (Impossibility of Crash Recovery)
エラーがOrchestratorに伝播しないことにより、自律システムの要である「自己修復（Self-healing）」プロセスが完全に麻痺しています。
OrchestratorはWorkerの生死を観測（Observability）できないため、以下のような基本的な回復アクションを一切トリガーできません。
- **Retry（再試行）**: 一過性のエラーと見なしてコンテキストをリセットし、別ワーカーを立ち上げる。
- **Fallback（代替手段）**: 異なるアプローチ・プロンプト・ツールを用いてタスクの解決を図る。
- **Escalation（人間へのエスカレーション）**: ユーザーに「Agentがクラッシュしたため指示・介入が必要」と助けを求める。

## 4. MUSTレベルの技術的負債と解決要件 (MUST-Level Debts & Requirements)
「Thin Orchestrator + Blackboard (PubSub)」アーキテクチャへの移行にあたり、以下の負債解消をMUST要件としてシステムに組み込む必要があります。

1. **Lifecycle Supervisorの導入 (Observability Debt)**
   - **要件**: エージェントプロセスを監視するスーパーバイザ（あるいはサイドカー）を導入すること。サブエージェントが異常終了した場合、インフラ側がWorkerに代わって即座に「AgentCrashed / TaskFailed」イベントをBlackboard（PubSub）または Orchestrator へ発行する仕組みを構築する。
2. **Timeout / Deadline管理の強制 (Resilience Debt)**
   - **要件**: Orchestratorがタスクを委譲・イベントを待機する際、無限待機を禁止し、必ず「実行期限（SLA）」を設けること。タイマー機能（`schedule` ツールの活用等）を利用し、タイムアウト超過時には強制的にタスクをキャンセルし、回復シーケンス（Retry / Escalate）へ移行するWatchdogパターンを標準化する。
3. **エラーコンテキストの永続化と Dead Letter Queue (DLQ)**
   - **要件**: クラッシュ時に失われる「どこまで思考・実行していたか」のトレース情報を保護するため、状態遷移や直前のログを State API / DB に細かく同期させる。また、処理不能に陥ったタスクイベントを退避する Dead Letter Queue (DLQ) を設け、後からの事後分析（Post-mortem）を可能にする。
