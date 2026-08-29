# 02. 移行戦略 (段階的ロールアウト - 最終版)

## 1. 概要
このドキュメントは、従来の `progress.md` ファイルベースの状態管理から、新しい SQLAlchemy ベースの `agent_tasks` DB (Task Registry) へ移行するための段階的な計画を定義します。
厳格なピアレビューに基づき、データロスを完全に防ぐための堅牢なロールバック戦略、状態調停（Reconciliation）メカニズム、そして静止フェーズ（Quiesce）を組み込んでいます。

## 2. 移行フェーズ

### フェーズ 1: TO-BE 構築 (開発)
- `core-service` に `agent_system` ドメインを実装します。
- CLIツール `manage_agent_task.py` を作成します。
- **逆マイグレーションツール**: DBから `progress.md` を生成する `export-to-file` コマンドを実装し、障害時のロールバックパスを確保します。

### フェーズ 2: 試運転 (Shadowing & Dual Write)
- **状態調停を伴うDual Write**: Agentは引き続き `progress.md` を更新します。裏でバックグラウンドフックが `manage_agent_task.py sync-from-file` を実行し、ファイルの状態を正本としてDBを強制的に上書き・同期させます。
- DBをまだ正本（SSOT）とは信用せず、実際の負荷環境で Watchdog API (`cleanup_stale_tasks`) などの動作を検証します。

### フェーズ 3: カナリアリリース (部分移行)
- 1つのワークスペースを「カナリア（実験台）」として選択します。
- **[重要] Quiesce (静止) フェーズ**: 
  - そのワークスペース内で現在稼働中のAgentがいないこと（`IN_PROGRESS == 0`）を確実に確認します。
  - 最後の `sync-from-file` を実行して、最新の状態をDBにフラッシュします。
- その後、`progress.md` を `.progress.md.bak` にリネームします（※削除はしません）。
- **ロールバックプロトコル**: もしカナリア環境で障害が起きた場合は、`manage_agent_task.py export-to-file` を使って**最新のDB状態から**新しい `progress.md` を生成し直して復旧します。単に `.bak` ファイルを戻すとDBで進んだ作業が失われるため、`.bak` はDB自体が完全に破損した際の最終手段としてのみ使用します。

### フェーズ 4: 完全移行とルールの引き算 (Cutover)
- すべてのワークスペースでグローバルな静止点（Quiesce）を確認した後、`migrate_progress_to_db.py` を実行して残りの全ファイルをDBに流し込みます。
- すべての `progress.md` を `.progress.md.bak` にリネームします。
- ルールの引き算（`03_Rule_Reduction_Plan.md` 参照）を実行します。
