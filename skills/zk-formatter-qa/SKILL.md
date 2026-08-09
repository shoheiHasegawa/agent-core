---
name: zk-formatter-qa
description: 対話ログからZettelkastenの設計原則（テンプレート・リンク規則）に従ったMarkdown原稿を生成するTier 2スキル。
---

# Skill: Zettelkasten Formatter QA

## 🎯 目的
対話ログから、Zettelkastenの設計原則に従ったPermanent Noteを生成・正規化する。

## 🏛️ アーキテクチャ (Tier & Execution Model)
- **Tier**: Subagent
- **モデル**: **flash**

## 🧠 ルールのJITロードとフォーマット自動正規化 (Normalization)
対象となる対話ログを、`agent-core/docs/rules/zettelkasten_heuristics.md` からJITロードしたルール（YAMLメタデータ、双方向リンク、抽象度）に従って自動的にクレンジング・正規化せよ。

**メタ認知 (Whyの維持)**:
フォーマットは厳格に守りつつも、「ユーザーの生々しい表現や『棘』」までAI特有の平滑化された文章に丸めてしまわないこと。「形式は整えるが、魂（コンテキストの熱量）は抜かない」というメタ認知を働かせること。

## 🛠️ 実行手順

### Step 1: 正規化・原稿生成 (Normalization)
*   **Action**: 対話ログを読み込み、上記ルールに従ってMarkdown原稿を生成・正規化する。

### Step 2: 自己QAチェック (Quality Assurance)
*   **Constraints**: YAMLタグの漏れ、双方向リンクの書式、抽象度が保たれているかを確認する。

### Step 3: 納品と報告 (Reporting)
*   **Action**: 完成したMarkdownテキストを出力とし、標準ワーカー報告フォーマットで親エージェントに完了を報告する。自身でファイルシステムへの書き込みは行わないこと。
