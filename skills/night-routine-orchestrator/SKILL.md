---
name: night-routine-orchestrator
description: 1日の終わりに行う内省と明日への準備を統括するOrchestrator（Tier 1）スキル。各フェーズのスキルを順次読み込み、Role Switchingによって対話を進行する。
type: Orchestrator
model: pro
---

# SKILL: Night Routine

このファイルは、特定のタスクを実行するための具体的な手法（Layer 3）を定義する。

## 🎯 目的 (ミクロな WHY)
1日の実績回収からカウンセリング、明日のタスク計画までの一連のルーティンを、状態（Role）を切り替えながら順次進行させるため。

## 📥 入力と出力 (ミクロな WHAT)
- **Input**: 1日の終わりのルーティン開始指示、`Briefing.md`
- **Output**: Inboxの整理、内省ログの記録、タスクスケジュールの更新、セッション終了の通知

## 🛠️ 実行手順 (HOW)

### 1. ワークログの回収
1. `uv run python3 agent-core/tools/sync_worklogs.py "agent-core/Briefing_YYYY-MM-DD.md"` を実行して本日の実績を回収する。
2. ユーザーに挨拶し、本日の進捗を共有して Phase 2 の状態へ移行する。

### 2. Inbox Triage (Phase 1)
1. `agent-core/skills/inbox-facilitator/SKILL.md` をJITロードする。
2. その手順に従いInboxの仕分け業務を完遂する。

### 3. Counseling (Phase 2)
1. `agent-core/skills/journaling-facilitator/SKILL.md` をJITロードする。
2. その手順に従いカウンセリング業務を完遂する。

### 3.5. 摩擦と失敗のSense Making抽出 (Phase 2.5)
1. ユーザーに対して「今日直面したシステムとの摩擦（ヤクの毛刈り）や、作業中の失敗・気づき」をヒアリングする（Triageで退避したLevel 2/3のBacklogの振り返りも含む）。
2. 得られた「気づき」や「失敗の教訓」を、将来のマネタイズや自己成長の種として `second-brain` の `sense_making` 領域（または該当するInbox）へMarkdownノートとして出力・ストックする。

### 4. Task Planning (Phase 3)
1. `agent-core/skills/priority-facilitator/SKILL.md` をJITロードする。
2. その手順に従い明日へのタスク計画と更新を完遂する。

### 5. クロージング (Phase 4)
1. 必要に応じてカレンダー同期ジョブを実行する。
2. ユーザーに明日の準備完了と、カレンダーが自動最新化される旨を通知する。
3. [完了条件 / Exit Criteria]: 標準ワーカー報告フォーマットで処理完了結果を報告し、OSセッションを終了する。
