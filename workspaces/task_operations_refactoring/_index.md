# Workspace: Task Operations Refactoring

- **ステータス**: `COMPLETED`
- **目的**: `TaskOperationsService` および `RefineTaskUseCase` / `RegisterTaskUseCase` の空洞化解消、6大観点SDD/TDD適用、CLI拡張、エラーハンドリング統一。
- **完了日**: 2026-08-03
- **成果物**:
  - `core-service/src/application/task_operations/spec.md` (6大観点 SSOT)
  - `core-service/src/application/task_operations/` (UseCase 実装・DI 化)
  - `core-service/tests/integration/task_operations/test_integration.py` (実DB 6大観点テスト)
  - `agent-core/tools/update_task.py` (CLI 引数拡張)
  - `core-service/docs/rules/error_handling.md` (例外設計正本)
