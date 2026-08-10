---
name: sdd-loop-orchestrator
description: 承認済み仕様書（spec.md）を受け取り、ダブルループTDD（Outer Red -> Inner TDD -> Quality Gate -> Compliance Review）の自律サイクルを統括・完走するTier 1オーケストレーター（Loop 2担当）。
type: Orchestrator
model: pro
---

# SKILL: SDD Loop Orchestrator

このファイルは、特定のタスクを実行するための具体的な手法（Layer 3）を定義する。

## 🎯 目的 (ミクロな WHY)
仕様書に沿ったTDDサイクルをサブエージェントに委譲しながら回し、品質ゲートとルールレビューを物理検証として用いることで、コードベースを安全に完成させるため。

## 📥 入力と出力 (ミクロな WHAT)
- **Input**: ユーザー承認済みの仕様書 (`spec.md`)
- **Output**: テストパス・品質ゲート通過・レビュー合格済みのGitコミット

## 🛠️ 実行手順 (HOW)

### Phase 1: Outer Red (Acceptance Test Creation)
1. `invoke_subagent` を用いて `tdd-red-builder` を起動し、`spec.md` を渡し結合テスト（またはバグ再現テスト）を作成させる。
2. `uv run python ../agent-core/tools/verify_loop_state.py --phase outer-red --target <test_file_path>` を実行し合否を判定する。
3. 成功（意図通りのアサーションまたは未実装エラー）なら、`tasks/progress.md` に記録しPhase 2へ。
4. スタブ起因の致命的エラー（`AttributeError` / `TypeError`）の場合は、スタブ作成元へ差し戻して型シグネチャを修正させる。

### Phase 2: Inner Loop & Green (Implementation & Unit Test)
1. `invoke_subagent` を用いて `tdd-green-refactorer` を起動し、実装と単体テストの補強を行わせる。
2. `uv run python ../agent-core/tools/verify_loop_state.py --phase green` を実行し判定する。
3. 成功ならPhase 3へ。失敗時はエラーログを添えて `tdd-green-refactorer` に再委譲する。

### Phase 3: Quality Gate Verification
1. `make check-all` を実行する。
2. 失敗した場合、エラーの原因仮説を言語化し、エラーログと共に `tdd-green-refactorer` へ差し戻す。
3. `tasks/progress.md` の `[Retry Count: N/3]` を更新する（最大3回まで）。3回失敗時は人間へエスカレーションして停止する。
4. 成功ならPhase 4へ。

### Phase 4: Compliance Review
1. `invoke_subagent` を用いて `compliance-reviewer` を起動する。
2. `spec.md` と実装コードの間に意味的な矛盾がないかレビューさせる。
3. Rejectされた場合は指摘事項をサニタイズしてPhase 2 (`tdd-green-refactorer`) へ差し戻す。
4. 成功ならPhase 5へ。

### Phase 5: Atomic Commit & Progress Update
1. `git add` および `git commit` を実行する。
2. ワークスペースの `tasks/progress.md` のチェックリストを更新する。
3. [完了条件 / Exit Criteria]: 完了報告（標準ワーカー報告フォーマット）を通知する。
