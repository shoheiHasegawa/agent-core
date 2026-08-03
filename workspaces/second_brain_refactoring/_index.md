# Workspace: Second Brain Refactoring

- **ステータス**: `READY`
- **目的**: `core-service/src/application/second_brain/` パッケージ（Inbox, Permanent, Sense-Making ノート登録、検索、Zettelkasten ルール検証）に対する 6大観点 SDD / TDD 適用と技術的負債解消。
- **対象コンポーネント**:
  - `src/application/second_brain/` (`register_inbox_note`, `register_permanent_note`, `register_sense_making_note`, `search_notes`, `audit_zettelkasten_rules`, `second_brain_service`)
  - `src/domain/second_brain/`
  - `src/infrastructure/local_file/local_file_second_brain_gateway.py`
  - `agent-core/tools/register_zettelkasten_note.py`
  - `agent-core/skills/zk-*`
