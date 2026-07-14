---
epic_name: Epic 03 (Action & Reflection Pipeline)
workspace_dir: Proj_Action_Reflection_Pipeline
status: IN_PROGRESS
next_action: "ルーティンタスクの棚卸しと、脳内の未完了タスクの回収"
---

# Handoff Packet: Proj_Action_Reflection_Pipeline

このパケットは、次に起動したAgentに「どのワークスペースを引き継ぐべきか」を伝える軽量なルーティングチケットです。

## 📍 次のAgentへの指示
1. `workspaces/Proj_Action_Reflection_Pipeline/` ディレクトリに移動してください。
2. その中の `tasks/progress.md` (残タスク) と `tasks/context.md` (現在の議論の焦点) を読み込んでください。
3. 読み込みが完了し、コンテキストを復元できたら、このパケット (`agent-core/queue/handoff_Proj_Action_Reflection_Pipeline.md`) を破棄（削除）して、ユーザーにタスク再開を提案してください。
