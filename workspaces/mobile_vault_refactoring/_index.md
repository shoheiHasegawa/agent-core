# Workspace: Mobile Vault Refactoring

- **ステータス**: `READY`
- **目的**: `core-service/src/application/mobile_vault/` パッケージ（Inbox アイテム Peek、処理・振り分け Process、ダッシュボード配信 Place）に対する 6大観点 SDD / TDD 適用と技術的負債解消。
- **対象コンポーネント**:
  - `src/application/mobile_vault/` (`peek_inbox_usecase`, `process_inbox_item_usecase`, `place_dashboard_usecase`, `mobile_vault_service`)
  - `src/domain/mobile_vault/`
  - `src/infrastructure/local_file/local_file_mobile_vault_gateway.py`
  - `agent-core/tools/peek_mobile_inbox.py`
  - `agent-core/skills/inbox-triage`
