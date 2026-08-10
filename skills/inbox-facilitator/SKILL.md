---
name: inbox-facilitator
description: Mobile Inboxから未処理InboxItemをPeekし、ユーザーと壁打ちを行ってTask Registryやアイデアノートに振り分け・回収するスキル。
type: Worker
model: pro
---

# SKILL: Inbox Triage

## 🎯 目的 (ミクロな WHY)
外部（iPhone等）から投函され Mobile Vault に溜まっている未処理のメモ（InboxItem）を直接読み取り、ユーザーとの対話を通して「それが何であるか」を解釈し、適切な場所に振り分けて保存・回収するため。（※AIが勝手に推測して登録せず、対話することでユーザーのメタ認知を促すため）

## 📥 入力と出力 (ミクロな WHAT)
- **Input**: Mobile Inbox内の未処理InboxItem
- **Output**: InboxItemの分類結果（Task, Idea, 削除, スキップ）および対応するコマンド実行

## 🛠️ 実行手順 (HOW)
1. `python3 agent-core/tools/peek_inbox.py` を実行し、未処理のInboxItem一覧と内容を取得する。（InboxItemがない場合は「本日の未処理メモはありません」とユーザーに伝えて終了する）
2. `agent-core/docs/rules/dialog_heuristics.md` をJITロードする。
3. 取得したメモ1件について、JITロードしたヒューリスティクスを踏み台にして、ユーザーと対話し分類と次アクションの合意を得る。（「ユーザーはなぜこのメモを残したのか？」を推論し、曖昧な場合はメタ認知を促す問いを行う。モバイル側に残すと判断された場合はスキップする。）
4. ユーザーから合意が得られた分類内容に基づき、`agent-core/tools/process_inbox_item.py` を用いて一気に処理を実行する。（Ideaの場合は `--action idea`、Taskの場合は `--action task`、削除の場合は `--action delete` を指定。スキップの場合は実行しない。）
5. すべての処理が終わったら、標準ワーカー報告フォーマットで完了報告を行う。
