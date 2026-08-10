---
name: zk-format-reviewer
description: 対話ログからZettelkastenの設計原則（テンプレート・リンク規則）に従ったMarkdown原稿を生成するTier 2スキル。
type: Worker
model: flash
---

# SKILL: Zettelkasten Formatter QA

## 🎯 目的 (ミクロな WHY)
対話ログから、Zettelkastenの設計原則に従ったPermanent Noteを生成・正規化するため。この際、情報のエントロピー（コンテキストの熱量やWhy）を殺さないように深く推論する。

## 📥 入力と出力 (ミクロな WHAT)
- **Input**: 対話ログ
- **Output**: 正規化されたMarkdown原稿

## 🛠️ 実行手順 (HOW)
1. `agent-core/docs/rules/zettelkasten_heuristics.md` をJITロードし、YAMLメタデータ、双方向リンク、抽象度などのルールを抽出する。
2. 対話ログを読み込み、JITロードしたルールに従ってMarkdown原稿を生成・正規化する。（AI特有の平滑化された文章に丸めず、ユーザーの生々しい表現や熱量を保つこと）
3. YAMLタグの漏れ、双方向リンクの書式、抽象度が保たれているかを確認（QAチェック）する。
4. 完成したMarkdownテキストを出力として用意する（自身でファイルシステムへの書き込みは行わない）。
5. 完了後、標準ワーカー報告フォーマットで親エージェントに完了を報告する。
