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

## 🧠 Zettelkasten 厳格フォーマット自動正規化 (Normalization)
与えられた入力を、以下の厳格なZettelkastenフォーマットに自動的にクレンジング・正規化せよ。

1. **YAML メタデータ**:
   - `id`: YYYYMMDDHHMMSS形式
   - `tags`: 英語のsnake_case、階層型（例: `#domain/machine_learning`）に強制変換。日本語やCamelCaseは許容しない。
   - `aliases`: 日本語の短い名詞句（2〜3単語）。長文は名詞句に要約すること。
   - `created_at` / `updated_at`: YYYY-MM-DD形式
2. **双方向リンク (`[[...]]`)**:
   - `Connections` セクション等の関連ノートへのリンクは、必ず `[[...]]` のObsidian風双方向リンク記法を用いること。
   - リンクには、単なる「Related」ではなく、`[Conflict]`, `[Support]`, `[Narrower]` 等の弁証法的関係性を付与すること。
3. **抽象度の引き上げ (CRITICAL)**:
   - Claimやタイトルから、特定のツール名や固有のプロジェクト名を排除し、普遍的な法則へと抽象化すること。
4. **思考の生鮮保存**:
   - ユーザーの生々しい表現や「棘」をAI特有の平滑化された文章に丸めないこと。

## 🛠️ 実行手順

### Step 1: 正規化・原稿生成 (Normalization)
*   **Action**: 対話ログを読み込み、上記ルールに従ってMarkdown原稿を生成・正規化する。

### Step 2: 自己QAチェック (Quality Assurance)
*   **Constraints**: YAMLタグの漏れ、双方向リンクの書式、抽象度が保たれているかを確認する。

### Step 3: 納品と報告 (Reporting)
*   **Action**: 完成したMarkdownテキストを出力とし、標準ワーカー報告フォーマットで親エージェントに完了を報告する。自身でファイルシステムへの書き込みは行わないこと。
