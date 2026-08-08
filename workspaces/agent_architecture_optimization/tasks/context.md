# 📍 Current Context (Working Memory)

> **⚠️ Agentへの絶対ルール**
> - このファイルは**最大50行以内**に保つこと。
> - ユーザーに返答する前に、必ず自律的にこのファイルを最新の文脈に上書き（Update）すること。

---

## 🎯 現在の焦点 (Current Focus)
- **PR 1 (Event Bus 移行 & DI整合)**: 完了・テスト全通過・コミット完了。
- **PR 2: クリーンネス自動検証ハーネス (`verify_cleanliness.py`) の構築** に着手。

## 📌 次の実行内容 (PR 2)
- `agent-core/tools/verify_cleanliness.py` の実装
  - 50行制限検証（`context.md` ≤ 50 lines）
  - 孤立ゴミ検知（`scratch/` 以外の不要ファイル等）
  - パス構造検証（`_index.md`, `tasks/progress.md`, `tasks/context.md`）
- `agent-core/scripts/pre_handoff_verify.sh` への統合と動作検証

## ❓ なぜ今ここにいるのか (Why we are here)
- 次のスキル改修（PR 4）やワークスペース移行（PR 5）を機械的に監視・保証する物理的ハーネスを先に構築するため。
