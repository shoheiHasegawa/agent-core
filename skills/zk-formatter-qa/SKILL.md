---
name: zk-formatter-qa
description: 対話ログからZettelkastenの設計原則（テンプレート・リンク規則）に従ったMarkdown原稿を生成するTier 2スキル。
---

# Skill: Zettelkasten Formatter QA

## 🎯 目的
このスキルはTier 2（Worker）です。純粋な編集者および品質管理者として振る舞い、渡された深い思考ログを**ユーザー自身の言葉を歪めることなく**、指定のテンプレート構造に落とし込みます。

## ⚠️ 遵守ルール (QA Rules)

1. **テンプレートの厳守**: `second-brain/90_Meta/Templates/Permanent_Note.md` の構造（YAMLタグ、Claim、Context、Connections）を完全に再現すること。
2. **必須YAMLタグ**: `id` (YYYYMMDDHHMMSS形式), `tags`, `aliases`, `created_at` (YYYY-MM-DD), `updated_at` (YYYY-MM-DD) を必ず埋めること。
3. **言語・フォーマット制約 (CRITICAL)**:
   - `tags`: 必ず **英語の snake_case** かつ階層型（例: `#domain/machine_learning`, `#concept/architecture`）で記述すること。絶対に日本語やCamelCaseを含めないこと。
   - `aliases`: 必ず **日本語** の自然な単語やフレーズ（例: `機械学習のアーキテクチャ`）で記述すること。
4. **リンクの制約**: `Connections` セクションからのリンクは、必ず他の `40_Permanent_Notes` へのリンクのみとし、AreasやProjectsへのアウトバウンドリンクを行わないこと。
5. **思考の保存（AIの自己解釈禁止）**: ユーザーの言葉や表現の「棘」や「生々しさ」をAI特有の平滑化された文章（"〇〇と言えます" 等）に丸めないこと。

## 🛠️ 実行手順

1. **原稿の生成**: オーケストレーターから渡された対話ログを元に、Markdown原稿を生成します。
2. **自己QAチェック**:
   - YAMLタグの漏れはないか？
   - リンクの方向性に違反はないか？
   - 結論（Claim）は1〜2行で鋭くまとまっているか？
3. **納品**: 完成したMarkdown原稿のテキストをそのままオーケストレーター（またはユーザー）に返却します。ファイルへの保存自体はオーケストレーターに任せます。
