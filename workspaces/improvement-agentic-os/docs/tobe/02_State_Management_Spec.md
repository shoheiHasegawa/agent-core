# 状態管理システム仕様 (Real TO-BE)

## 1. 概要
このドキュメントは、脆いファイルベースの `progress.md` アプローチを置き換える、TO-BEの状態管理システムについて概説します。
実際の `core-service` コードベースに基づき、既存のSQLAlchemyインフラを活用したAgent OSプロセス専用のTask Registry (`agent_tasks`) を導入します。

## 2. 目標と主な要件
- **ACID準拠とCAS**: `UPDATE ... WHERE status='PENDING'` を介したCompare-and-Swap (CAS) を使用し、タスク状態のアトミックな更新を保証します。
- **ドメインの隔離**: Agentのタスクを人間のタスク（`task_management` ドメイン）から分離します。
- **対話ベースのトリガー**: 複雑なバックグラウンドのWatchdogを構築するのではなく、フロントAgentがタスクのトリガーと監視を担います。

## 3. データベーススキーマ (`agent_tasks`)

Task Registryは、SQLAlchemy経由で既存のDB（`you_inc_ops.db`）等に構築されます。

### テーブル: `agent_tasks`
| カラム名      | データ型  | 制約                        | 説明                                                               |
|---------------|-----------|-----------------------------|--------------------------------------------------------------------|
| `id`          | String    | PRIMARY KEY                 | タスクの一意な識別子。                                             |
| `command`     | String    | NOT NULL                    | サブエージェントに対する指示（プロンプト）。                       |
| `status`      | String    | NOT NULL, DEFAULT 'PENDING' | 現在の状態: `PENDING`, `IN_PROGRESS`, `COMPLETED`, `FAILED`.       |
| `assigned_to` | String    | NULLABLE                    | 現在タスクを処理しているWorkerのID。                               |
| `created_at`  | DateTime  | NOT NULL, DEFAULT NOW()     | タスクが作成された日時。                                           |
| `updated_at`  | DateTime  | NOT NULL, DEFAULT NOW()     | レコードが最後に更新された日時。                                   |
| `result_data` | String    | NULLABLE                    | 完了時の出力データや成果物へのリンク。                             |

### 並行性制御 (CAS)
`scratch/spike_cas.py` にてテスト・実証済み:
```python
result = session.query(AgentTask).filter(
    AgentTask.id == task_id,
    AgentTask.status == "PENDING"
).update({
    "status": "IN_PROGRESS",
    "assigned_to": worker_id,
    "updated_at": now
})
```
もし `result == 0` となった場合、別のAgentがすでにそのタスクを取得していることを意味し、競合が完全に防がれます。
