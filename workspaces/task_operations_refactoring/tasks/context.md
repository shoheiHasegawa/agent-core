# Current Context (RAM)

- 現在地: Loop 1（Discovery: 協働仕様策定）
- 対象: `core-service/src/application/task_operations/`
- 主な論点:
  1. `RefineTaskUseCase` でどのようなパラメータ（title, estimated_minutes, category, deadline, is_deep_work, memo, description等）の更新を許可するか。
  2. `RegisterTaskUseCase` の `uuid.uuid4()` 直書き解消と `UuidGenerator` DI。
  3. `Task` エンティティにおける `description` / `last_memo` / `area_id` の整合性。
  4. 6大観点テストシナリオの定義。
