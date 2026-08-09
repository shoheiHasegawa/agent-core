---
name: zk-distillation-orchestrator
description: Zettelkastenのノート蒸留作業を統括し、検索から対話のリード、ワーカーの呼び出しまでをオーケストレーションするTier 1スキル。
---

# Skill: Zettelkasten Distillation Orchestrator (Model: 親 Orchestrator / Pro)

## 🎯 目的
このスキルはTier 1（Orchestrator）です。アトミックノート蒸留境界（一過性のメモから普遍的法則 Permanent Note を抽出するフィルタリング基準）を管理し、自身がソクラテス対話をリードしつつ、QAやフォーマットは適切なTier 2サブエージェントに委譲してノートを完成させます。

## 🛠️ 実行手順

### 1. 文脈の取得と再構築の判断 (Context Retrieval & Restructuring)
*   **入力 (Input)**: ユーザーから渡された「蒸留待ちメモ」やキーワード
*   **アクション (Action)**: 壁打ちを開始する**前**に、必ず `agent-core/tools/search_zettelkasten.py` 等で `40_Permanent_Notes` を検索し、「対立・矛盾（Conflict）」や「強力な支持・根拠（Support）」となる対立軸を探す。
*   **制約事項 (Constraints)**: 既存ノートを発見した場合、フォーマットと抽象度を監査し、要件を満たさない場合は既存ノート自体の再構築（上書き・リネーム）を行う計画を立てること。
*   **出力 (Output)**: 検索で得られた「既存ノートの文脈（矛盾や関連性）」を次のフェーズ（Socratic Interviewer）の初期プロンプトへ引き継ぐ。

### 2. ルールのJITロードと深掘り対話のリード (Socratic Interview)
*   **入力 (Input)**: 初期メモとフェーズ1で取得した既存ノートの文脈
*   **アクション (Action)**: `agent-core/docs/rules/zettelkasten_distillation.md` （アトミックノート蒸留境界の基準）をJITロードし、オーケストレーター自身が `socratic-interviewer` の役割を兼任してユーザーとソクラテス対話を実施する。
*   **メタ認知と揺らぎ (Whyの注入)**: 
    - JITロードした蒸留基準を踏み台として、「これは一過性の事実か、それとも普遍的な法則か？」を問いかける。
    - もしユーザーが局所的な最適化（特定のプロジェクトだけの話）に囚われていると感じたら、「それが他のドメイン（例えばXXX）でも通用するとしたら、どう表現できますか？」というメタ認知を促し、抽象度を強制的に引き上げること。
*   **出力 (Output)**: ユーザーとの深い対話ログ、および抽出された普遍的法則のドラフト

### 3. 品質管理とフォーマット化の委譲 (QA & Formatting)
*   **入力 (Input)**: 完了した対話ログ
*   **アクション (Action)**: 「`zk-formatter-qa`」スキルを持たせたサブエージェントを起動し、「対話ログから新規Permanent Noteの最終原稿を作成せよ」と指示する。
*   **制約事項 (Constraints)**: もしStep 1で既存ノートとの衝突や抽象度の不足が確認されていた場合、**必ず既存ノートの再定義（アップデート）原稿もセットで作成させること。**
*   **出力 (Output)**: 生成されたMarkdown原稿（新規ノート用＋既存ノート修正用）

### 3.5. 人間のプレビュー・承認（Approval）
*   **入力 (Input)**: QAエージェントが作成した原稿
*   **アクション (Action)**: ユーザーにMarkdownのプレビュー（既存ノートを修正する場合はその差分も）を提示する。
*   **制約事項 (Constraints)**: いきなりファイルへ書き込んではならない。必ず「この内容で新規保存／上書きしてよいか」の承認を得ること。
*   **出力 (Output)**: ユーザーからの承認 (Approve)

### 4. 最終保存と検証 (Final Commit)
*   **入力 (Input)**: 承認済みのMarkdown原稿
*   **アクション (Action)**: 原稿を `second-brain/40_Permanent_Notes/` に保存する。その後、**必ず**元となったインキュベーションメモ（`20_Sense_Making`等）を `rm` コマンド等で削除し、Gitへのコミットおよびプッシュまで完了させる。
*   **制約事項 (Constraints)**: 保存時は直接ファイルに書き込まず、必ず `agent-core/tools/register_zettelkasten_note.py --type permanent ...` を用いること。
*   **出力 (Output)**: `check_zettelkasten.py` によるCI結果。パスしない場合は再修正。
