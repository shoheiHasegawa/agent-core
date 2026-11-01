# 📍 Current Context (Working Memory)

> **⚠️ Agentへの絶対ルール**
> - このファイルは**最大50行以内**に保つこと。これを超える場合は古い情報を要約圧縮、または削除すること。
> - 対話ログのコピペは禁止。Agent自身の言葉で抽象化・要約したメタ認知情報のみを記載すること。
> - ユーザーに返答する前に、必ず自律的にこのファイルを最新の文脈に上書き（Update）すること。

---

## 🎯 現在の焦点 (Current Focus / Handoff Point)
- アーキテクチャ実装・`main` マージ・Worktree回収・Timeless SSOT化・Linter仕組み化まで100%完了。
- **次セッションでの最終クローズ条件（残り3ステップ）**:
  1. **GitHub Issue 起票ルールの壁打ち・定義**: どこのリポジトリに、どの粒度・フォーマット（`WHY ➔ WHAT [DoD] ➔ HOW`）で起票し、どう `backlog/` と使い分けるかを合意する。
  2. **やり残し課題の実際の Issue 起票 (`gh issue create`)**:
     - 候補①：`core-service` 内の旧 SQLite タスク管理ドメイン（`task_operations` / `daily_planning` / `agent_task`）の引き算整理
     - 候補②：OSレベル完全隔離サンドボックス（Docker / DevContainer）対応
     - 候補③：PC（Antigravity 秘書）からの Google Calendar / Tasks 直接連携
  3. **クローズ時の知識蒸留（ルートB — `second-brain`）**:
     - 今回の社長の核心的気づき（`WHY ➔ WHAT ➔ HOW` の思考の型、引き算ファースト、ブラックボックス化を防ぐ内省タッチポイント、上流の曖昧さのブルウィップ効果と2-Passループ）を壁打ちして Permanent Note / Sense Making Note へ蒸留する。

## 📌 完了済み基盤サマリー
- **3リポジトリ統一 & Timeless SSOT**: `agent-core`, `core-service`, `second-brain` すべてで `README.md` / `AGENTS.md` / [`docs/architecture.md`](../../../docs/architecture.md) を `WHY ➔ WHAT ➔ HOW` 構造に統一。
- **機械的ガードレール**:
  - [`audit_skills.py`](../../../tools/audit_skills.py): 正本ドキュメントの `WHY` 欠如および時系列ノイズ混入を pre-commit / `make check-all` で自動ブロック。
  - [`workspace_manager.py`](../../../tools/workspace_manager.py): `make ws-harvest` 時に独立レビュアーの `scratch/review_report.md` (`PASS`) が無ければ回収を物理拒否。
