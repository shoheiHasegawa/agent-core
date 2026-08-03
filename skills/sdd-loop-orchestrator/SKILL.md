---
name: sdd-loop-orchestrator
description: 承認済み仕様書（spec.md）を受け取り、ダブルループTDD（Outer Red -> Inner TDD -> Quality Gate -> Compliance Review）の自律サイクルを統括・完走するTier 1オーケストレーター（Loop 2担当）。
---

# Skill: SDD Loop Orchestrator (Loop 2: Autonomous TDD Execution)

## 🎯 目的
ユーザー承認済みの仕様書（`spec.md`）を受け取り、各専門職ワーカー（サブエージェント）を順序正しく召喚し、機械的な品質ゲート（Exit Code）による物理判定と自律修復（Self-Healing）を行いながら、完全自律で高品質なコードベースを完成・コミットする。

## ⚠️ 絶対遵守ルール
1. **職務分離（Tier 1の不干渉）**: オーケストレーター自身はプロダクションコード（`src/`）やテストコード（`tests/`）を直接編集してはならない。必ずサブエージェント（`invoke_subagent`）に委譲せよ。
2. **自己申告の禁止（Exit Code による物理判定）**: ワーカーの「完了しました」という言葉を信じるな。必ず `agent-core/tools/verify_loop_state.py` の物理実行結果で合否を判定せよ。
3. **自律差し戻し（Self-Healing Loop）**: テスト失敗や品質ゲート違反が発生した場合は、エラーログを添えて直前のワーカーに差し戻せ（最大3回リトライ）。

---

## 🛠️ 実行手順

```mermaid
graph TD
    P1[Phase 1: Outer Red] --> P2[Phase 2: Inner Loop Green]
    P1 -- Stub/Signature Error --> S1[Phase 1 回帰: spec.md/スタブ修正]
    P2 -- Green Verified --> P3[Phase 3: Quality Gate make check-all]
    P3 -- Quality Fail Max 3 --> P2
    P3 -- Quality Pass --> P4[Phase 4: Compliance Review]
    P4 -- Review Reject --> P2
    P4 -- Review Pass --> P5[Phase 5: Atomic Commit & Handoff]
```

### Phase 1: Outer Red (Acceptance Test Creation)
*   **入力 (Input)**: ユーザー承認済みの `spec.md`
*   **アクション (Action)**: `invoke_subagent` を用いて `tdd-red-coder` を起動。`spec.md` を渡し、`tests/integration/<domain>/` 配下に結合テストを作成させる（バグ修正時はバグ再現テスト）。
*   **検証 (Gate Check)**:
    ```bash
    uv run python ../agent-core/tools/verify_loop_state.py --phase outer-red --target <test_file_path>
    ```
*   **判定 & ルーティング**:
    - `success: true`（意図通りのアサーションまたは未実装エラー）: `tasks/progress.md` に Proof of Red を記録して Phase 2 へ。
    - **スタブ起因の致命的エラー（`AttributeError` / `TypeError` in `src/`）の場合**: `tdd-red-coder` ではなく、スタブ作成元へ差し戻して型シグネチャを修正。

### Phase 2: Inner Loop & Green (Implementation & Unit Test)
*   **入力 (Input)**: `spec.md` と `tests/integration/` のテストパス
*   **アクション (Action)**: `invoke_subagent` を用いて `tdd-green-refactorer` を起動。実装および `tests/unit/` の単体テスト補強を行わせる。
*   **検証 (Gate Check)**:
    ```bash
    uv run python ../agent-core/tools/verify_loop_state.py --phase green
    ```
*   **判定**: `success: true` であれば Phase 3 へ。失敗時はエラーログを添えて `tdd-green-refactorer` に再委譲。

### Phase 3: Quality Gate Verification ( make check-all )
*   **アクション (Action)**:
    ```bash
    make check-all
    ```
*   **制約事項 (Constraints)**: カバレッジ >= 90%、Ruff lint/format、AST双方向トレーサビリティ検証がすべて Exit 0 であること。
*   **自律修復 (Prompt Sanitization & Max 3 Retries)**:
    - 失敗時は「①対象ファイルパス ②git diff ③エラー末尾50行」のみを抽出して `tdd-green-refactorer` に渡す。3回連続で失敗した場合は人間にエスカレーションする。

### Phase 4: Independent Compliance Review
*   **アクション (Action)**: `invoke_subagent` を用いて `compliance-reviewer` を起動し、合憲性・ルール審査を行わせる。
*   **制約事項 (Constraints)**: 
    - レビューで指摘・Reject された場合は、指摘事項をサニタイズして Phase 2 (`tdd-green-refactorer`) へ差し戻す。
    - **【完全ループバック原則】**: 修正後は必ず **Phase 2 (Green) ➔ Phase 3 (Quality Gate) ➔ Phase 4 (Review)** を再走し、デグレがないことを再検証すること。

### Phase 5: Atomic Commit & Progress Update
*   **アクション (Action)**:
    - `git add` および `git commit` を実行。
    - ワークスペースの `tasks/progress.md` のチェックリストを更新し、完了報告を行う。
*   **出力 (Output)**: 完全検証済みのコミットハッシュおよび進捗完了レポート。
