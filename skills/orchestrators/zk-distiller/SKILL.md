---
name: zk-distiller
description: ソクラテス式の問いかけで社長の思考・内省（ルートBの学び）を深掘りし、生々しい熱量（Why）を保ったまま Zettelkasten のノートへ蒸留・保存するスキル。
model: pro
type: Orchestrator
---

# SKILL: Zettelkasten Distiller (内省・知識蒸留ファシリテーター)

## 🎯 目的 (WHY)
日々の意思決定やプロジェクト完遂（ルートBの還流）、または `Mobile Vault` の着想メモから、社長自身の頭を通して普遍的な知見を引き出し、熱量（Whyのエントロピー）を殺さずに `second-brain` の資産へ変換するため。

## 📥 入力と出力の契約 (I/O Contract)
- **Input**: 社長の気づき・着想メモ・プロジェクト振り返りのトピック、および `agent-core/docs/rules/zettelkasten_and_dialog_principles.md`
- **Output**: 社長承認済みの Zettelkasten ノート（`20_Sense_Making` または `40_Permanent_Notes`）の登録とリンク整合性検証パス

## 🛠️ 実行手順 (HOW)

### 1. 既存知識の探索とソクラテス式壁打ち (Socratic Dialogue)
1. `second-brain/40_Permanent_Notes/` や `20_Sense_Making/` を検索し、関連する過去のノートや思考の文脈を特定する。
2. いきなりAIが答えを書いてまとめるのではなく、**「なぜそう感じたのか？」「一見〇〇に見えるが、本質は△△だとしたらどうなるか？」「他の領域にも言える普遍的な構造は何か？」** という問いを1〜2問投げかけ、社長自身の言葉を引き出す。

### 2. 熱量（Whyのエントロピー）を保つドラフト作成 ([EXP-06] 準拠)
1. `agent-core/docs/rules/zettelkasten_and_dialog_principles.md` のフォーマット・双方向リンク規則に従い、ノートのドラフトを作成する。
2. **絶対制約**: AI特有の教科書的で無難な要約に丸めてはならない。社長が語った生々しい表現、トレードオフの葛藤、具体例をそのまま核として残すこと。

### 3. 承認と公式CLIによる登録
1. ドラフト（既存ノート更新時はその差分）を社長に提示し、承認を得る。
2. 承認後、`core-service` の公式CLIを実行して保存する（※直接のファイル作成・編集は厳禁）：
   ```bash
   cd core-service && PYTHONPATH=src uv run python -m entrypoints.cli.main zk-register \
     --type permanent \
     --title "<タイトル>" \
     --content "<Claimの内容>" \
     --context "<Contextの内容>" \
     --tags "<tag1,tag2>" \
     --links "<link1,link2>"
   ```
3. 登録後、リンク切れやフォーマット違反がないことを確認して完了する。
