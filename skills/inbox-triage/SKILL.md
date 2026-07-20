---
name: inbox-triage
description: Inboxの未処理パケットを回収し、ユーザーと壁打ちを行ってTask Registryやアイデアノートに振り分ける仕分け（Worker）スキル。
---

# Skill: Inbox Triage (Worker)

## 🎯 目的
外部（iPhone等）から投函され `agent-core/queue/` に溜まっている未処理のメモ（パケット）を読み取り、ユーザーとの対話を通して「それが何であるか（TaskかIdeaか）」を解釈し、適切な場所に振り分けて保存する。

## ⚠️ 実行ルール
*   **推測で勝手に登録しない**: 曖昧なメモであっても、AIが勝手に解釈してタスク登録してはならない。必ずユーザーに提案・確認（壁打ち）を行うこと。
*   **1パケットずつ確実に処理する**: 一度に大量に処理してユーザーを混乱させない。

## 🛠️ 実行手順

### 1. Queueのバッチ読み取り
*   **アクション (Action)**: `python3 agent-core/tools/read_inbox_queue.py --limit 5` を実行し、未処理のパケットを最大5件取得する。
*   **出力 (Output)**: 未処理パケットのリスト（※パケットがない場合は「本日の未処理メモはありません」とユーザーに伝えて終了する）

### 2. ユーザーへのArtifact（Triage Plan）提示
*   **入力 (Input)**: 取得した未処理パケット
*   **アクション (Action)**: 各パケットに対して推論・清書を行い、**`triage_plan.md` というArtifact**を作成してユーザーに提示する。（チャット内で1件ずつ壁打ちしないこと）
*   **制約事項 (Constraints)**: 以下の書式例に従い、推測で勝手に登録しないこと。
    - 削除: `packet_xxx`
    - Inboxへ登録: タイトル案, タグ案 (`domain/..., concept/...` の形式厳守), プレビュー
    - タスク化: タイトル案, Properties (`[Must, 30m]`等)。※必ずタスク内容から「深い思考や集中を要するもの（High）」か「単純作業や連絡（Low）」かを自動推測し、`energy_level` プロパティ（High または Low）を付与すること。
*   **出力 (Output)**: ユーザーからのArtifactに対する修正指示や「OK（承認）」

### 3. パケットの一括処理実行
*   **入力 (Input)**: ユーザーから合意が得られた Triage Plan
*   **アクション (Action)**: 承認されたパケットに対して以下のコマンドを一気に実行する。
    *   **アイデアとして保存**:
        一時ファイル（scratch/）を利用して本文を渡し、確実に `process_queue_packet.py` 経由で登録・削除・Gitコミットを行わせること。
        ```bash
        cat << 'EOF' > scratch/temp_idea.md
        (ここに清書した本文を流し込む)
        EOF
        python3 agent-core/tools/process_queue_packet.py --packet_name "packet_xxx" --action idea --title "タイトル" --tags "domain/xxx, concept/yyy" --body_file "scratch/temp_idea.md"
        rm scratch/temp_idea.md
        ```
    *   **タスク化**: `python3 agent-core/tools/process_queue_packet.py --packet_name "packet_xxx" --action task ... --energy_level "High/Lowのいずれか"`
    *   **削除**: `python3 agent-core/tools/process_queue_packet.py --packet_name "packet_xxx" --action delete`
*   **制約事項 (Constraints)**: LLMが生成した長文を処理する際は、コマンドライン引数のエスケープエラーを防ぐため必ず `scratch/` に一時ファイルを作成して `--body_file` に渡し、処理後は確実に一時ファイルを削除（Leave No Trace）してください。

### 4. 完了報告
*   **アクション (Action)**: すべてのパケット処理が終わったら「本日のInboxの仕分けがすべて完了しました。」と報告する。
*   **出力 (Output)**: 次のフェーズへの移行（終了）
