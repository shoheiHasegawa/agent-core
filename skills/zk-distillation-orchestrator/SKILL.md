---
name: zk-distillation-orchestrator
description: Zettelkastenのノート蒸留作業を統括し、検索からワーカーの呼び出しまでをオーケストレーションするTier 1スキル。
---

# Skill: Zettelkasten Distillation Orchestrator

## 🎯 目的
このスキルはTier 1（Orchestrator）です。自身で深い考察やファイル編集を行わず、全体の手順を管理し、適切なツールとTier 2サブエージェントを呼び出してPermanent Noteを完成させます。

## 🛠️ 実行フロー

### 1. 文脈の取得と再構築の判断 (Context Retrieval & Restructuring)
*   **アクション (絶対制約)**: 壁打ち（Socratic Interview）を開始する**前**に、必ず `agent-core/tools/search_zettelkasten.py` や検索ツールを実行し、`40_Permanent_Notes` 内から関連する既存ノートを探してください。単なる類似ノートだけでなく、**「対立・矛盾（Conflict）」や「強力な支持・根拠（Support）」となる強い対立軸を必ず探索すること**。
*   **制約**: 既存ノートを発見した場合、単にリンクを追記するだけで済ませてはなりません。「既存ノートが最新のフォーマット（3部構成）と普遍的な抽象度を保っているか」を監査し、要件を満たさない場合は既存ノート自体の再構築（上書き・リネーム）を行う計画を立ててください。
*   **インタビュアーへの引き継ぎ**: 検索で得られた「既存ノートの文脈（特に矛盾や関連性）」を、必ず次のフェーズのSocratic Interviewerへの初期プロンプトに含めて渡してください。

### 2. 深掘り対話の委譲 (Socratic Interview)
*   **アクション**: `define_subagent` および `invoke_subagent` を使い、「`socratic-interviewer`」スキルを持たせたサブエージェントを起動します。
*   **指示**: 「この初期メモと、既存ノートの文脈を渡すので、ユーザーと壁打ちをして洞察を深めてください」と指示します。

### 3. 品質管理とフォーマット化の委譲 (QA & Formatting)
*   **アクション**: 対話が完了（ユーザーが満足）したら、対話ログをまとめて「`zk-formatter-qa`」スキルを持たせた別のサブエージェントを起動します。
*   **指示**: 「この対話ログから、Permanent Noteのテンプレートに従って最終原稿を作成し、CI基準を満たしているかチェックしてください」と指示します。

### 3.5. 人間のプレビュー・承認（Approval）
*   **アクション**: QAエージェントが作成した原稿をいきなりファイルへ書き込んではいけません。必ずユーザーにMarkdownのプレビューを提示し、「この内容で保存してよいか」の承認（Approve）を得てください。

### 4. 最終保存と検証 (Final Commit)
*   **アクション**: ユーザーの承認後、原稿を `second-brain/40_Permanent_Notes/` に保存します。その後、**必ず**元となったインキュベーションメモ（`20_Sense_Making`等の蒸留元ファイル）を `rm` コマンド等で削除し、Gitへのコミットおよびプッシュまでをセットで完了させてください。
*   **絶対制約**: 新規ノートの保存時、Agentが直接OSのツールを用いて `40_Permanent_Notes/` に書き込むことは禁止されています。必ず `agent-core/tools/register_zettelkasten_note.py --type permanent ...` を用いて保存してください。（※元ファイルの削除とGitコマンドの実行はターミナルから行って構いません）
*   **検証**: 保存後、必ず `agent-core/tools/check_zettelkasten.py` を実行し、CI（静的解析）をパスするか確認します。パスしない場合は自身で修正を行うか、QAエージェントに再修正させます。
