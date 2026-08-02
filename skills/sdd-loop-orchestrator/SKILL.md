---
name: sdd-loop-orchestrator
description: SDDとダブルループTDD（Outer Red -> Inner TDD -> Quality Gate -> Review）の自律サイクルを統括・実行するTier 1オーケストレーター。
---

# Skill: SDD Loop Orchestrator (Tier 1)

## 🎯 目的
ユーザーからの要求を受け、各専門職ワーカー（サブエージェント）を順序正しく召喚し、機械的な品質ゲート（Exit Code）による物理判定と自律差し戻し（Self-Healing）を行いながら、完全自律で高品質なコードベースを完成させる。

## ⚠️ 絶対遵守ルール
1. **職務分離（Tier 1の不干渉）**: オーケストレーター自身はプロダクションコード（`src/`）やテストコード（`tests/`）を直接編集してはならない。必ずサブエージェント（`invoke_subagent`）に委譲せよ。
2. **自己申告の禁止（Exit Code による物理判定）**: ワーカーの「完了しました」という言葉を信じるな。必ず `agent-core/tools/verify_loop_state.py` の物理実行結果で合否を判定せよ。
3. **自律差し戻し（Self-Healing Loop）**: テスト失敗や品質ゲート違反が発生した場合は、エラーログを添えて直前のワーカーに差し戻せ（最大3回リトライ）。

---

## 🛠️ 実行手順

```
[Phase 1: Spec Design] -> sdd-spec-writer (spec.md 作成)
         │
         ▼
[Phase 2: Outer Red]   -> tdd-red-coder (tests/integration/ 結合テスト作成)
         │                └─ verify_loop_state.py --phase outer-red で検証
         ▼
[Phase 3: Inner Loop]  -> tdd-green-refactorer (src/ 実装 & tests/unit/ 補強)
         │                └─ verify_loop_state.py --phase green で検証
         ▼
[Phase 4: Quality Gate]-> verify_loop_state.py --phase quality (カバレッジ >= 90%)
         │                └─ FAIL時は Phase 3 へエラー付きで差し戻し
         ▼
[Phase 5: Review]      -> compliance-reviewer (独立司法による合憲性・ルール審査)
         │                └─ 指摘時は Phase 3 へ修正委譲
         ▼
[Phase 6: Commit]      -> Git Commit & progress.md 更新
```

### Phase 1: SDD Spec Design
*   **Action**: `invoke_subagent` を用いて `sdd-spec-writer` を起動し、対象機能の `spec.md` を作成させる。
*   **Output**: 確定した `spec.md` のパス（例: `src/application/<domain>/spec.md`）と、定義された要求ID一覧。

### Phase 2: Outer Red (Acceptance Test)
*   **Action**: `invoke_subagent` を用いて `tdd-red-coder` を起動。`spec.md` を渡し、`tests/integration/<domain>/` 配下に結合テストを作成させる。
*   **Context Handoff**: `tdd-red-coder` から「作成したテストファイルパス（例: `tests/integration/task_management/test_auto_assign.py`）」を返却値として受け取る。
*   **Gate Check**:
    ```bash
    uv run python ../agent-core/tools/verify_loop_state.py --phase outer-red --target <test_file_path>
    ```
*   **判定 & Proof of Red 証跡記録**: 
    - `success: true`（意図通りのアサーションまたは未実装エラー）の場合:
      - レスポンス内の `proof_of_red` メタデータを取得。
      - `tasks/progress.md` のチェックリストに `- [x] Proof of Red: <target> (<failure_type> at <verified_at>)` を記録して Phase 3 へ。
    - 構文エラーやPASSしてしまった場合は `tdd-red-coder` に修正を再委譲。

### Phase 3: Inner Loop & Green (Implementation & Unit Test)
*   **Action**: `invoke_subagent` を用いて `tdd-green-refactorer` を起動。`spec.md` と `tests/integration/` のテストパスを渡し、実装および `tests/unit/` の単体テスト補強を行わせる。
*   **Gate Check**:
    ```bash
    # 1. 新規テストのパス確認
    uv run python ../agent-core/tools/verify_loop_state.py --phase green --target <test_file_path>
    # 2. 全体テストのパス（リグレッション・デグレがないことの検証）
    uv run python ../agent-core/tools/verify_loop_state.py --phase green
    ```
*   **判定**: 両方が `success: true` であれば Phase 4 へ。失敗時はエラーログを添えて `tdd-green-refactorer` に修正を指示。

### Phase 4: Quality Gate Verification (司法)
*   **Gate Check**:
    ```bash
    uv run python ../agent-core/tools/verify_loop_state.py --phase quality
    ```
*   **判定 & 自律修復ループ (Max 3 Retries / Prompt Sanitization)**: 
    - `success: true`（カバレッジ >= 90%、Makefile完全性、トレーサビリティ全一致、Linter通過）であれば Phase 5 へ。
    - `success: false` の場合:
      - **The "God Prompt" 予防（プロンプト・サニタイズ）**: 会話履歴全文を渡さず、以下の3点のみを抽出して `tdd-green-refactorer` に渡す。
        1. 修正対象ファイルパス一覧
        2. 最新の `git diff`
        3. `verify_loop_state.py` が返したエラー末尾50行（`details`）
      - **エスカレーション**: 3回連続で解決できない場合は自律ループを停止し、発生したエラーログと原因分析をユーザーに報告して介入を仰ぐこと。

### Phase 5: Independent Compliance Review
*   **Action**: `invoke_subagent` を用いて `compliance-reviewer` を起動し、DDD/SOLID/Context Engineeringの観点で独立レビューを行わせる。
*   **判定**: 指摘事項があれば `tdd-green-refactorer` に修正させ、Passであれば Phase 6 へ。

### Phase 6: Atomic Commit & Progress Update
*   **Action**: 
    - `git add` および `git commit` を実行（Pre-commit hook が自動検証）。
    - ワークスペースの `tasks/progress.md` のチェックリストを更新し、完了報告を行う。
