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
  - ユースケースの実装 (`register_task_usecase.py`, `checkout_task_usecase.py`, `complete_task_usecase.py`, `fail_task_usecase.py`) を完成。
  - **アーキテクチャ是正 (DDD Refactoring)**: 当初 `sqlite3` の生実装で作成したためシステム全体のDI・SQLAlchemyのエコシステムと矛盾が発生。その後、正しく `infrastructure/sqlalchemy/agent_task_repository.py` へ移行し、さらに完全なDDD準拠（Entityにおける `updated_at` ベースの楽観的ロック CAS、Rich Domain Model、Repositoryの抽象化）へのリファクタリングを完了。
  - 全ての検証ゲートウェイ (`validate_sdd.py`, `make check-all`) をオールグリーンで通過 (Coverage 93.5%).

## ユーザーとの合意事項（最重要）
- **DBの物理配置**: まったく新しいDBファイルを作成するのではなく、**既存の `you_inc_ops.db` に新しいテーブル (`agent_tasks`) を追加** することで実装する。テーブル名（論理層）で完全に独立させる。

---

## 完了したフェーズ (Phase 6: CLI / Interface Integration)
- `manage_agent_task.py` (JSON-First Protocol準拠のCLIツール) の実装。
- `you_inc_ops.db` に対するE2Eでの追加・チェックアウト・完了・失敗の動作検証。
- DB初期化スクリプト `init_db.py` の分離と `app_context.py` のクリーン化。
- テスト稼働用ワーカー `agent-task-worker` SKILL の作成。

---

## 次にやるべき作業 (次セッションでの「試運転」とマイグレーション)
次のセッション（または引き継いだAgent）はここから開始すること。

1. **実戦投入テスト（試運転）**
   新システムを用いて、以下の2つの小さいタスクをWorker（サブエージェント）に並行処理させる。
   - タスク1: このトピック（Phase 1〜6）で作成した一時ファイルや作業の残骸を調査・削除する。
   - タスク2: このトピックで実装したソースやドキュメントが記載ルール（AGENT.md等）に則っているかレビューし、必要なら修正する。
   - **実行手順**: フロントAgentが上記タスクを `manage_agent_task.py --json '{"action": "add"}'` で登録し、`agent-task-worker` を持たせたサブエージェントを2体起動して完了を待つこと。
2. **既存ルールのマイグレーション (Phase 6 - Step 3)**
   試運転完了後、`AGENT.md` や既存の `SKILL.md` 内に残っている旧来のタスク管理ルールや呼び出しを削除し、新しいCLIツールとシステムを利用するようにルーティングを繋ぎ変える。

---

## 📝 Technical Debt (Backlog)
- **Level 2**: `core-service` 全体への Unit of Work パターンの導入と、全 Repository からの `commit()` 排他。
  - 現状、各Repository（`SqlAgentTaskRepository`, `SqlTaskRepository`等）が内部で直接 `session.commit()` を呼んでいるため、Application層が複数のリポジトリを跨ぐトランザクション境界を制御できていない。将来の Maintenance モードで一括リファクタリングを推奨。
