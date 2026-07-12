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

## 🛠️ 実行手順（対話フロー）

### Step 1: Queueのバッチ読み取り
`python3 agent-core/tools/read_inbox_queue.py --limit 5` を実行し、未処理のパケットを最大5件取得する。
※パケットがない場合は、「本日の未処理メモはありません」とユーザーに伝えて終了（フェーズ完了）する。

### Step 2: ユーザーへのArtifact（Triage Plan）提示
チャットのメッセージ内で1件ずつ壁打ちするのではなく、取得した（最大）5件のパケットに対してあなたが推論・清書を行い、**`triage_plan.md` というArtifact**を作成してユーザーに提示する。

**Artifact (`triage_plan.md`) の書式例:**
```markdown
- [ ] `packet_xxx`: **削除**（テストデータのため）
- [x] `packet_yyy`: **Inboxへ登録**
  - タイトル案: ...
  - タグ案: `domain/..., concept/...`
  - プレビュー（清書案）: ...
- [x] `packet_zzz`: **タスク化**
  - タイトル案: ...
  - Properties: `[Must, High Energy, 30m]`
```

ユーザーがArtifactを確認し、修正指示や「OK（承認）」を出したら次のステップへ進む。
**【重要: タグの命名規則】**
提案するタグは、必ず英語のsnake_caseかつ階層型（例: `domain/business_development`, `concept/autonomous_agent` 等）で記述すること。絶対に日本語やCamelCaseを含めない。

**☑️ タスクとして登録する場合**:
以下のプロパティをユーザーと壁打ち（または妥当な推測を提示して合意）すること。
1. **Title** (タスク名)
2. **Category** (`M`=Must, `S`=Should, `W`=Want)
3. **Energy Level** (`High`, `Medium`, `Low`)
4. **Estimated Minutes** (所要時間の目安・分)

### Step 3: パケットの一括処理実行
ユーザーからTriage Planの合意が得られたら、承認されたパケットに対して一気に以下のコマンドを実行する。

*   **アイデアとして保存する場合 (一時ファイル不要・標準入力利用)**:
    LLMが生成した長文を処理する際、一時ファイルを残さない（Leave No Trace）ため、インメモリ（ヒアドキュメント）で直接ツールに流し込むこと。
    ※エスケープ漏れ等の実行リスクについては、Agentが事前コミットやバックアップを行っていることで担保する。
       ```bash
       cat << 'EOF' | python3 agent-core/tools/register_zettelkasten_note.py --type inbox --title "タイトル" --tags "domain/xxx, concept/yyy"
       (ここに清書した本文を流し込む)
       EOF
       
       # 保存が成功したら、パケットを削除
       rm -rf agent-core/queue/packet_xxx
       ```
*   **タスクとして登録する場合**:
    `python3 agent-core/tools/process_queue_packet.py --packet_name "packet_xxx" --action task --title "タイトル" --category "M" --energy_level "High" --estimated_minutes 30`
*   **削除（破棄）する場合**:
    `python3 agent-core/tools/process_queue_packet.py --packet_name "packet_xxx" --action delete`

コマンド実行後、エラーがなければ次のパケットの処理（Step 2）へ移る。

### Step 4: 完了報告
すべてのパケットの処理が終わったら、「本日のInboxの仕分けがすべて完了しました。」と報告し、次のフェーズ（ジャーナリング等）を促して終了する。
