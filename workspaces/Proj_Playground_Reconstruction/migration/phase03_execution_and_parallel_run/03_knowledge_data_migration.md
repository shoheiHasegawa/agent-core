# 03_knowledge_data_migration.md

## 目的
純粋なナレッジデータを新 `second-brain` へ移行し、新たなInboxルーティングフローの運用を開始する。

## タスクリスト

### 1. 知識データの抽出と移行
- [ ] Phase 02 で仕分けた Permanent Notes（普遍的な知識）のみを、新 `second-brain` リポジトリへ移行する。
- [ ] 移行対象外としたプロジェクトの実行ログ（`progress.md`等）は、`agent-core` の管理下（`epics/` 等）へ移動させる。

### 2. Inboxルーティングの再構築
- [ ] `agent-core` 上に InboxTriageAgent をデプロイし、処理ルールを設定する。
- [ ] `mobile-vault` (iCloud等) から入力されたメモが、内容に応じて 新 `second-brain/00_Inbox` または `agent-core/epics/` に正しく仕分け（ルーティング）されることをテストする。

### 3. フロントエンド（View）の再設定
- [ ] `obsidian-view` の設定（`.obsidian` やダッシュボード生成設定）を `90_Meta/` 配下に集約し、新 `second-brain` 向けの表示が正常に行えるか確認する。

## 成果物
- 移行完了後の新 `second-brain` データ
- 稼働確認済みのInboxルーティング基盤
