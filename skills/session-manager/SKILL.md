---
name: session-manager
description: Agentic OSのセッション開始時（起動シーケンス）および終了時（ハンドオフ）の進捗管理とルーティングを行うスキル。
type: Orchestrator
model: pro
---

# SKILL: Session Manager

このファイルは、特定のタスクを実行するための具体的な手法（Layer 3）を定義する。

## 🎯 目的 (ミクロな WHY)
セッション開始時のコンテキスト復元と終了時の状態保存を標準化し、エージェントがスムーズに作業を再開・引き継ぎできるようにするため。

## 📥 入力と出力 (ミクロな WHAT)
- **Input**: ワークスペース内の `tasks/context.md`、`tasks/progress.md`、またはセッション終了・中断の指示
- **Output**: 適切なスキルの起動、状態ファイルの更新、またはGitコミットによる終了状態の保存

## 🛠️ 実行手順 (HOW)

### 1. 起動シーケンス (Bootstrapping)
1. 対象のリポジトリや直近の会話から、現在アクティブなプロジェクト（Epic）または作業中のタスクが存在するかを検証する。
2. 対象ワークスペースの `tasks/context.md` を読み込み、前回の文脈と直近のFocusを把握する。
3. `tasks/progress.md` を読み込み、現在の進捗（Loop状態）を確認する。
4. `progress.md` の現在地に応じた適切なスキルをルーティング（起動）する。
   - 「Loop 1: 仕様策定中」の場合 ➔ `sdd-spec-builder` を起動
   - 「Loop 2: 自律TDD実装中」の場合 ➔ `sdd-loop-orchestrator` を起動

### 2. セッション中の状態維持
1. セッション中の対話や議論の結論に基づき、自律的に `tasks/progress.md` と `tasks/context.md` を更新する。

### 3. セッション終了・申し送り (Handoff)
1. `tasks/progress.md` の `## 💡 Session Insights` に未登録（`[ ]`）の知見があるかスキャンする。
2. 存在する場合、ユーザーにZettelkastenへの登録を提案する。承認されたら `register_zettelkasten_note.py` を実行し、`progress.md` 側を `[x]` に更新する。
3. `tasks/context.md` に次回の論点（Current Focus）を書き残す。
4. `bash tools/pre_handoff_verify.sh` を実行し、検証に合格することを確認する。
5. 成功後、`git add . && git commit -m "chore: Handoff - [作業のサマリ]" && git push` を実行する。
6. [完了条件 / Exit Criteria]: Gitの同期が完了し、ユーザーへハンドオフが完了したことを通知する。
