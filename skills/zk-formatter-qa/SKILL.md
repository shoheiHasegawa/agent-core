---
name: zk-formatter-qa
description: 対話ログからZettelkastenの設計原則（テンプレート・リンク規則）に従ったMarkdown原稿を生成するTier 2スキル。
---

# Skill: Zettelkasten Formatter QA

## 🎯 目的
このスキルはTier 2（Worker）です。純粋な編集者および品質管理者として振る舞い、渡された深い思考ログを**ユーザー自身の言葉を歪めることなく**、指定のテンプレート構造に落とし込みます。

## ⚠️ 遵守ルール (QA Rules)

1. **テンプレートの厳守**: `second-brain/90_Meta/Templates/Permanent_Note.md` の構造（YAMLタグ、Claim、Context、Connections）を完全に再現すること。
2. **抽象度の厳格な担保 (CRITICAL)**: タイトル（ファイル名）および `Claim` には、特定のツール名（例: RAG, node_modules等）やプロジェクト固有の「具象」を含めてはなりません。時代やツールが変わっても通用する「普遍的な法則・アーキテクチャ」へと抽象度を引き上げること。
3. **必須YAMLタグ**: `id` (YYYYMMDDHHMMSS形式), `tags`, `aliases`, `created_at` (YYYY-MM-DD), `updated_at` (YYYY-MM-DD) を必ず埋めること。
4. **言語・フォーマット制約 (CRITICAL)**:
   - `tags`: 必ず **英語の snake_case** かつ階層型（例: `#domain/machine_learning`, `#concept/architecture`）で記述すること。絶対に日本語やCamelCaseを含めないこと。
   - `aliases`: 必ず **日本語** の短い名詞句（2〜3単語程度）で記述すること。絶対に長文（文節以上の長さ）にしないこと。（例: `機械学習のアーキテクチャ`）
5. **リンクの制約**: `Connections` セクションからのリンクは、必ず他の `40_Permanent_Notes` へのリンクのみとし、単に「Related」で済ますのではなく、探索結果に基づく `[Conflict]` (対立・矛盾), `[Support]` (根拠・支持), `[Narrower]` (具体論) 等の弁証法的な関係性を必ず明記すること。
6. **思考の保存（AIの自己解釈禁止）**: ユーザーの言葉や表現の「棘」や「生々しさ」をAI特有の平滑化された文章（"〇〇と言えます" 等）に丸めないこと。

## 🛠️ 実行手順

1. **原稿の生成**: オーケストレーターから渡された対話ログを元に、Markdown原稿を生成します。
2. **自己QAチェック**:
   - YAMLタグの漏れはないか？
   - リンクの方向性に違反はないか？
   - 結論（Claim）は1〜2行で鋭くまとまっているか？
3. **納品**: 完成したMarkdown原稿のテキストをそのままオーケストレーター（またはユーザー）に返却します。ファイルへの保存自体はオーケストレーターに任せます。
