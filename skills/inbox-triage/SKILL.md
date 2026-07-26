---
name: inbox-triage
description: Mobile Inboxから未処理パケットをPeekし、ユーザーと壁打ちを行ってTask Registryやアイデアノートに振り分け・回収するスキル。
---

# Skill: Inbox Triage (Worker)

## 🎯 目的
外部（iPhone等）から投函され Mobile Vault に溜まっている未処理のメモ（パケット）を直接読み取り、ユーザーとの対話を通して「それが何であるか（TaskかIdeaか、モバイルに残すか）」を解釈し、適切な場所に振り分けて保存・回収する。

## ⚠️ 実行ルール
*   **推測で勝手に登録・回収しない**: 曖昧なメモであっても、AIが勝手に解釈してタスク登録してはならない。必ずユーザーに提案・確認（壁打ち）を行うこと。
*   **モバイル側に残す判断**: ユーザーが「これはトレード日誌だから残す」等と判断したものは、**何もアクションを実行せずスキップ**すること。そうすればモバイル側にそのまま残る。

## 🛠️ 実行手順

### 1. Mobile Inbox の Peek (覗き見)
*   **アクション (Action)**: `python3 agent-core/tools/peek_mobile_inbox.py` を実行し、未処理のパケット一覧と内容を取得する。
*   **出力 (Output)**: 未処理パケットのリスト（※パケットがない場合は「本日の未処理メモはありません」とユーザーに伝えて終了する）

### 2. ユーザーへのArtifact（Triage Plan）提示
*   **入力 (Input)**: 取得した未処理パケット
*   **アクション (Action)**: 各パケットに対して推論・清書を行い、**`triage_plan.md` というArtifact**を作成してユーザーに提示する。（チャット内で1件ずつ壁打ちしないこと）
*   **制約事項 (Constraints)**: 以下の書式例に従い、推測で勝手に登録しないこと。
    - 削除: `packet_xxx`
    - 残留(スキップ): `packet_xxx` (そのままモバイルに残す)
    - Idea登録: タイトル案, タグ案 (`domain/..., concept/...` の形式厳守), プレビュー
    - Task化: タイトル案, Properties (`[Must, 30m]`等)。※必ずタスク内容から「深い思考や集中を要するもの（High）」か「単純作業や連絡（Low）」かを自動推測し、`energy_level` プロパティ（High または Low）を付与すること。
*   **出力 (Output)**: ユーザーからのArtifactに対する修正指示や「OK（承認）」

### 3. パケットの一括処理実行 (Process & Fetch)
*   **入力 (Input)**: ユーザーから合意が得られた Triage Plan
*   **アクション (Action)**: 承認されたパケットに対して以下のコマンドを一気に実行する。（**※「残留(スキップ)」と判断されたパケットに対しては何も実行しないこと**）
    *   **アイデアとして保存 (Idea)**:
        `process_mobile_packet.py` を使用して対象のパケットIDを指定するだけで、自動的に関連画像を Second Brain の Attachments へ移動しつつアイデアノートとして登録される。一時ファイルの作成は不要（厳禁）。
        ```bash
        # Note: --title と --tags を指定して実行
        python3 agent-core/tools/process_mobile_packet.py --packet_id "packet_xxx.md" --action idea --title "タイトル" --tags "domain/xxx, concept/yyy"
        ```
    *   **タスク化 (Task)**:
        ```bash
        python3 agent-core/tools/process_mobile_packet.py --packet_id "packet_xxx.md" --action task --title "タイトル" --energy_level "High/Lowのいずれか"
        ```
    *   **削除 (Delete)**:
        ```bash
        python3 agent-core/tools/process_mobile_packet.py --packet_id "packet_xxx.md" --action delete
        ```

### 4. 完了報告
*   **アクション (Action)**: すべてのパケット処理が終わったら「本日のMobile Inboxのトリアージ・回収がすべて完了しました。」と報告する。
*   **出力 (Output)**: 次のフェーズへの移行（終了）
