---
name: zk-distillation-orchestrator
description: Zettelkastenのノート蒸留作業を統括し、検索からワーカーの呼び出しまでをオーケストレーションするTier 1スキル。
---

# Skill: Zettelkasten Distillation Orchestrator

## 🎯 目的
このスキルはTier 1（Orchestrator）です。自身で深い考察やファイル編集を行わず、全体の手順を管理し、適切なツールとTier 2サブエージェントを呼び出してPermanent Noteを完成させます。

## 🛠️ 実行フロー

### 1. 文脈の取得 (Context Retrieval)
*   **アクション**: ユーザーから渡された「蒸留待ちメモ（`20_Sense_Making`）」やキーワードを基に、`agent-core/scripts/search_zettelkasten.py` を実行して関連する既存ノートを探します。
*   **制約**: 必ずスクリプトを使い、コンテキストウィンドウを節約してください。

### 2. 深掘り対話の委譲 (Socratic Interview)
*   **アクション**: `define_subagent` および `invoke_subagent` を使い、「`socratic-interviewer`」スキルを持たせたサブエージェントを起動します。
*   **指示**: 「この初期メモと、既存ノートの文脈を渡すので、ユーザーと壁打ちをして洞察を深めてください」と指示します。

### 3. 品質管理とフォーマット化の委譲 (QA & Formatting)
*   **アクション**: 対話が完了（ユーザーが満足）したら、対話ログをまとめて「`zk-formatter-qa`」スキルを持たせた別のサブエージェントを起動します。
*   **指示**: 「この対話ログから、Permanent Noteのテンプレートに従って最終原稿を作成し、CI基準を満たしているかチェックしてください」と指示します。

### 4. 最終保存と検証 (Final Commit)
*   **アクション**: QAエージェントから上がってきた原稿を `second-brain/40_Permanent_Notes/` にMarkdownファイルとして保存します。
*   **検証**: 保存後、必ず `agent-core/scripts/check_zettelkasten.py` を実行し、CI（静的解析）をパスするか確認します。パスしない場合はQAエージェントに再修正させます。
