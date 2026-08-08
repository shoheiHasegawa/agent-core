# 📍 Current Context (Working Memory)

> **⚠️ Agentへの絶対ルール**
> - このファイルは**最大50行以内**に保つこと。
> - ユーザーに返答する前に、必ず自律的にこのファイルを最新の文脈に上書き（Update）すること。

---

## 🎯 現在の焦点 (Current Focus)
- **PR 1 & PR 2**: 完了・テスト/クリーンネス全通過・コミット完了。
- **PR 3: サブエージェント契約テンプレート (`templates/Subagent_Prompt_Template.md`) の作成** に着手。

## 📌 次の実行内容 (PR 3)
- `agent-core/templates/Subagent_Prompt_Template.md` の新規作成
  - 【呼び出し契約 (Invocation Contract)】: 職務定義、明確なゴール、入力パラメータ（JITポインタ）、明示的制約
  - 【報告契約 (Reporting Contract)】: 担当タスク、変更/生成ファイル、検証ステータス (PASS/FAIL)、テスト/コマンド実行結果、要約
  - Flash ワーカーと Pro ワーカーの使い分け基準・Few-Shot 例を収録
- `audit_orphan_scripts.py` および `templates/README.md` 等での参照登録

## ❓ なぜ今ここにいるのか (Why we are here)
- PR 4 の全18スキル改修において、オーケストレーターからサブエージェントへの呼び出し品質を契約型で保証するため。
