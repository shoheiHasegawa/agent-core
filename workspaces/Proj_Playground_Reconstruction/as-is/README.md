# As-Is (現状と課題)

> [!CAUTION]
> **【ローカルルール：記載境界 (What & Bounds)】**
> - **What**: 変更を加える前の「現在のシステム状態」と、直面している「具体的な課題・ペインポイント」の純粋な事実のみを記録します。
> - **Bounds**: 解決策、あるべき姿（To-Be）、移行手順については**一切記載しないでください**。ここは「Where we are」のみを語る場所です。

本ディレクトリには、You, Inc. アーキテクチャ（3層分離）へ移行する前の、旧システムが抱えていた構造的課題とペインポイントが記録されています。

## 🗺️ アーカイブ一覧

1. **[01_architecture_and_pain_points.md](./01_architecture_and_pain_points.md)**
   - 旧リポジトリ（`life-automation` と `second-brain`）の密結合によるSRP違反や、Inboxの汚染、データと実行ロジックの混在など、根本的なアーキテクチャの課題を記録。
2. **[02_project_management_issues.md](./02_project_management_issues.md)**
   - PARAメソッド時代の `10_Projects` フォルダが「実行状態のGod Object」と化し、AIのコンテキストを圧迫・ハルシネーションを誘発していた運用上の限界を記録。
