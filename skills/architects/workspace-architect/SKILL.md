---
name: workspace-architect
description: プロジェクト（Epic）のワークスペースが公式ルールに準拠しているかを監視・強制し、構築から完了時のクリーンアップまでを管理するシステム・オーケストレーター。
type: Worker
model: flash
---

# SKILL: Workspace Architect

このファイルは、特定のタスクを実行するための具体的な手法（Layer 3）を定義する。

## 🎯 目的 (ミクロな WHY)
Epicの開始、作業中、終了時においてワークスペースのファイル構造を生成・検証し、常にクリーンな状態を保つため。

## 📥 入力と出力 (ミクロな WHAT)
- **Input**: Epicの新規開始要求、ワークスペースの監査要求、またはEpicの完了要求
- **Output**: ワークスペースディレクトリとファイルの生成、不要ファイルの隔離、またはZettelkastenへの退避とクリーンアップの完了

## 🛠️ 実行手順 (HOW)

### Case 1: Epicの新規開始 (Setup)
1. `agent-core/backlog/<Epic名>.md` が存在する場合は、その内容を読み取る。
2. `workspaces/<Epic名>/` ディレクトリを作成し、`_index.md`, `tasks/progress.md`, `tasks/context.md` の雛形を展開する。
3. `_index.md` にEpicの目的と概要（バックログの内容）を記載し、元の `backlog/<Epic名>.md` は削除する。

### Case 2: ワークスペースの監査と矯正 (Lint & Fix)
1. 作業中のワークスペースに対して `agent-core/tools/verify_cleanliness.py` などの自動化ツールを実行する。
2. 直下に落ちているファイルや一時的なゴミを発見した場合は、`scratch/` ディレクトリへ移動させる。

### Case 3: Epicの完了と教訓抽出 (Handoff & Sense-Making)
1. `docs/` 内の有益な設計書やルールを上位の保管庫（`agent-core/docs/` 等）への退避を提案・実行する。
2. 将来に活かせる普遍的な教訓やアンチパターンについてユーザーに問いかけ、Zettelkastenへの蒸留を促す。
3. ワークスペースディレクトリ全体（`workspaces/<Epic名>/`）を削除する。
5. 削除状態を再度Gitコミットし、クリーンな状態に戻す。
6. [完了条件 / Exit Criteria]: 標準ワーカー報告フォーマットで処理完了結果を報告する。
