# You_Inc システム改善プロジェクト (improvement-agentic-os) 進捗と引継ぎ

## 完了したフェーズ (Phase 1 〜 5)
- **現状分析 (As-Is)**: 複数Agentによる `progress.md` 競合やエラーTruncation問題の洗い出し。
- **アーキテクチャ設計 (To-Be)**: 
  - `agent_os.db` を用いた CAS (Compare-and-Swap) ロックによる排他制御タスク管理。
  - フロントAgentとWorker（サブエージェント）の Interactive Trigger による運用（自律的Watchdogの排除）。
- **マイグレーション・ルール改訂計画**: 
  - Dual Write および Quiesce (静止点) を設けた安全な段階的移行戦略。
  - 既存ルール (`AGENT.md`, `SKILL.md`) からソフト制約を剥がし、公式CLIツールへのルーティング（引き算）を確定。
  - すべてのドキュメントを対象に「Fact-Checking Loop」を実施し、ハルシネーション（嘘のルール等）を完全排除。
- **SDD (詳細仕様設計)**:
  - `core-service/src/application/agent_task/` 配下に `README.md` と `spec.md` (6大観点テストシナリオ等を含む) を配置。
  - Facadeとなる `agent_task_service.py` および各UseCaseのスタブを作成済み。
- **TDD Implementation (Phase 5)**:
  - `docs/spec/agent_task_system.md` の6大観点マトリクスのシナリオに基づくテスト (`test_agent_task.py`) を実装。
  - ユースケースの実装 (`add_task_usecase.py`, `checkout_task_usecase.py`, `complete_task_usecase.py`, `fail_task_usecase.py`) を完成。
  - `SqliteAgentTaskRepository` を実装し、テストをオールグリーンで通過。

## ユーザーとの合意事項（最重要）
- **DBの物理配置**: まったく新しいDBファイルを作成するのではなく、**既存の `you_inc_ops.db` に新しいテーブル (`agent_tasks`) を追加** することで実装する。テーブル名（論理層）で完全に独立させる。

---

## 次にやるべき作業 (Phase 6: CLI / Interface Integration)
次のセッション（または引き継いだAgent）はここから開始すること。

1. `agent-core/tools/` または `core-service/src/interfaces/cli/` 周辺にて、`AgentTaskService` を呼び出してタスクを管理するCLIツール (JSON-First Protocol準拠) またはインターフェースを実装する（`tool-architect` の領域）。
2. CLIからの動作検証と、実際のシステム (`you_inc_ops.db`) に対する結合検証を行う。
3. `AGENT.md` や `SKILL.md` 内で実際にそのツールを呼び出すようにマイグレーションを進める。
