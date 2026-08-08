---
name: inbox-triage
description: Mobile Inboxから未処理InboxItemをPeekし、ユーザーと壁打ちを行ってTask Registryやアイデアノートに振り分け・回収するスキル。
---

# Skill: Inbox Triage (Worker)

## 🎯 目的
外部（iPhone等）から投函され Mobile Vault に溜まっている未処理のメモ（InboxItem）を直接読み取り、ユーザーとの対話を通して「それが何であるか（TaskかIdeaか、モバイルに残すか）」を解釈し、適切な場所に振り分けて保存・回収する。

## ⚠️ 実行ルール
*   **推測で勝手に登録・回収しない**: 曖昧なメモであっても、AIが勝手に解釈してタスク登録してはならない。必ずユーザーに提案・確認（壁打ち）を行うこと。
*   **モバイル側に残す判断**: ユーザーが「これはトレード日誌だから残す」等と判断したものは、**何もアクションを実行せずスキップ**すること。そうすればモバイル側にそのまま残る。

## 🛠️ 実行手順

### 1. Mobile Inbox の Peek (覗き見)
*   **アクション (Action)**: `python3 agent-core/tools/peek_inbox.py` を実行し、未処理のInboxItem一覧と内容を取得する。
*   **出力 (Output)**: 未処理InboxItemのリスト（※InboxItemがない場合は「本日の未処理メモはありません」とユーザーに伝えて終了する）

### 2. ユーザーへのプラン提示と対話（2分トリアージ）
*   **入力 (Input)**: 取得した未処理InboxItem
*   **アクション (Action)**: 各InboxItemを「タスク（行動）」か「アイデア（知識）」かに二者択一で分類し、ユーザーに提案する。
*   **制約事項 (Constraints)**: 
    - **2分トリアージ**: 2分以内で完了できるタスクは、タスク化せずに「今すぐ終わらせてしまう」ことをユーザーに提案する。
    - **二者択一Few-Shot**:
        - Task (行動): 実行可能な動詞が含まれ、完了状態が定義できるもの。
        - Idea (知識): 実行ではなく、保管や結びつけが必要な概念。
    - **曖昧メモのラダーリング**: 判断に迷う一言メモは勝手に推論せず、「このメモは『〇〇というタスク』ですか？それとも『××に関するアイデア』ですか？」と一段階具体化（ラダーリング）して問いかける。
*   **出力 (Output)**: ユーザーとの対話を通じた分類の合意

### 3. InboxItemの一括処理実行 (Process & Fetch)
*   **入力 (Input)**: ユーザーから合意が得られた分類内容
*   **アクション (Action)**: 承認されたInboxItemに対して以下のコマンドを一気に実行する。（**※「残留(スキップ)」と判断されたInboxItemに対しては何も実行しないこと**）
    *   **アイデアとして保存 (Idea)**:
        `process_inbox_item.py` を使用して対象のInboxItemIDを指定するだけで、自動的に関連画像を Second Brain の Attachments へ移動しつつアイデアノートとして登録される。一時ファイルの作成は不要（厳禁）。
        ```bash
        # Note: --title と --tags を指定して実行
        python3 agent-core/tools/process_inbox_item.py --item_id "packet_xxx.md" --action idea --title "タイトル" --tags "domain/xxx, concept/yyy"
        ```
    *   **タスク化 (Task)**:
        ```bash
        python3 agent-core/tools/process_inbox_item.py --item_id "packet_xxx.md" --action task --title "タイトル" --energy_level "High/Lowのいずれか"
        ```
    *   **削除 (Delete)**:
        ```bash
        python3 agent-core/tools/process_inbox_item.py --item_id "packet_xxx.md" --action delete
        ```

### 4. 完了報告
*   **アクション (Action)**: すべてのInboxItem処理が終わったら「本日のMobile Inboxのトリアージ・回収がすべて完了しました。」と報告する。
*   **出力 (Output)**: 次のフェーズへの移行（終了）
