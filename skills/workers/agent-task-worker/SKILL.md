---
name: agent-task-worker
description: Agent Task をフェッチ（Checkout）し、実行して完了・失敗を報告するワーカースキル。自律的な無限ポーリングは行わず、イベントまたはフロントAgentからの明示的な指示（Interactive Trigger）によって起動される。
model: pro
type: Worker
---

# SKILL: Agent Task Worker

このファイルは、特定のタスクを実行するための具体的な手法（Layer 3）を定義する。
試運転目的の新規スキルとして実装されている。

## 🎯 目的 (ミクロな WHY)
- フロントAgentやイベントから呼び出された際に、DB上で `PENDING` 状態となっている Agent Task を1つ取得し、安全に実行（Checkout -> Execute -> Complete/Fail）するため。

## 📥 入力と出力 (ミクロな WHAT)
- **Input**: スキル呼び出し（定期実行または手動トリガー）
- **Output**: 対象タスクの状態遷移（COMPLETED または FAILED）および結果の保存

## 🛠️ 実行手順 (HOW)
1. `uv run python agent-core/tools/manage_agent_task.py --json '{"action": "checkout", "worker_id": "<your-agent-id>"}'` を実行し、アサイン可能なタスクを取得する。
2. 取得できたタスクがなければ終了する。
3. 取得できた場合、`command` の内容（タスクの指示内容）を読み解き、自身の持つツール（ファイル読み書き、コマンド実行、検索など）を駆使して自律的に目的を達成するための実作業を行う。
4. 処理が成功した場合: `uv run python agent-core/tools/manage_agent_task.py --json '{"action": "complete", "task_id": "<task_id>", "result_data": "..."}'`
5. 処理が失敗した場合: `uv run python agent-core/tools/manage_agent_task.py --json '{"action": "fail", "task_id": "<task_id>", "error_msg": "..."}'`
6. [完了条件 / Exit Criteria] 取得したタスクのステータス更新が完了すること。
7. 完了後、以下のフォーマットで親エージェントに結果を報告し、コンテキストを純粋に保つこと:
   ```
   【Task ID】: <task_id または None>
   【Result】: COMPLETED / FAILED / NO_TASK
   【Details】: <結果データ または エラーメッセージ>
   ```

## 🛑 制約 (Constraints)
- **メタ認知の深さへの特化 (Worker Principle)**: タスクそのものの必要性（広さ）を疑うことはOrchestratorに委ねる。当ワーカーは「実行する作業が真の意図（Why）やルールの本質に合致しているか？」という**「深さ」**に絞って推論を行い、盲目的な指示待ち作業者にならないこと。
