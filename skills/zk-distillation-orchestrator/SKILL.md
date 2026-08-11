---
name: zk-distillation-orchestrator
description: Zettelkastenのノート蒸留作業を統括し、検索から対話のリード、ワーカーの呼び出しまでをオーケストレーションするTier 1スキル。
type: Orchestrator
model: pro
---

# SKILL: Zettelkasten Distillation Orchestrator

このファイルは、特定のタスクを実行するための具体的な手法（Layer 3）を定義する。

## 🎯 目的 (ミクロな WHY)
一過性のメモを検索・対話・フォーマット化のパイプラインに通すことで、普遍的な Permanent Note として抽出・保存するため。

## 📥 入力と出力 (ミクロな WHAT)
- **Input**: 蒸留待ちメモ、または関連するキーワード
- **Output**: 承認済みのMarkdown原稿、および Zettelkasten への保存とGitコミット

## 🛠️ 実行手順 (HOW)

### 1. 文脈の取得 (Context Retrieval)
1. 汎用的な探索ツール（grep_search等）を用いて `40_Permanent_Notes` を検索し、関連するノートを特定する。
2. 既存ノートが発見された場合は、既存ノートの再構築（上書き・リネーム）計画を立て、抽出した文脈を次のフェーズへ引き継ぐ。

### 2. 対話のリード (Socratic Interview)
1. 未処理の Inbox または Sense-Making ノートを収集する（あるいはユーザーから渡されたノートを対象とする）。
2. 自身が `socratic-facilitator` の役割を担い、ユーザーとソクラテス対話を実施する。
3. 普遍的な法則のドラフトを抽出する。

### 3. QA & Formattingの委譲
1. サブエージェントを起動し、`zk-format-reviewer` スキルを実行させて対話ログから新規 Permanent Note の最終原稿を作成させる。
2. Step 1 で既存ノートの再構築が必要と判断した場合は、既存ノートの修正原稿もセットで作成させる。

### 4. プレビューと承認 (Approval)
1. ユーザーに作成されたMarkdownのプレビュー（既存ノート修正時はその差分も）を提示し、承認を求める。

### 5. 最終保存と検証 (Final Commit)
1. 承認後、`agent-core/tools/register_zettelkasten_note.py --type permanent ...` を実行してノートを保存する。
2. 元となったインキュベーションメモを削除し、Gitコミットとプッシュを行う。
3. [完了条件 / Exit Criteria]: `check_zettelkasten.py` 等によるCIパスを確認し、標準ワーカー報告フォーマットで処理完了結果を報告する。
