# Agent-Core Tools (Catalog)

本ディレクトリは、Agentic OS で利用されるステートレスなCLIツールの格納場所である。  
設計思想・JSON-First Protocol・運用ルールについては [tool_design_principles.md](file:///Users/shoheihasegawa/you_inc/agent-core/docs/rules/tool_design_principles.md) を参照せよ。

## 🛠️ ツール一覧 (Index)

| ツール名 | 種別 | 目的 (What / Why) |
| :--- | :--- | :--- |
| [`register_zettelkasten_note.py`](file:///Users/shoheihasegawa/you_inc/agent-core/tools/register_zettelkasten_note.py) | Write | Zettelkasten（Inbox / Sense-Making / Permanent）へのノート登録（JSON-First） |
| [`peek_inbox.py`](file:///Users/shoheihasegawa/you_inc/agent-core/tools/peek_inbox.py) | Read | Mobile Vault の未処理 Inbox アイテム取得 |
| [`process_inbox_item.py`](file:///Users/shoheihasegawa/you_inc/agent-core/tools/process_inbox_item.py) | Write | Inbox アイテムのタスク化・アイデア化・削除処理 |
| [`check_zettelkasten.py`](file:///Users/shoheihasegawa/you_inc/agent-core/tools/check_zettelkasten.py) | Audit | Zettelkasten のリンク・フォーマット整合性検証 |
| [`update_task.py`](file:///Users/shoheihasegawa/you_inc/agent-core/tools/update_task.py) | Write | Task Registry 内のタスク状態（Status, Priority等）の更新 |
| [`validate_sdd.py`](file:///Users/shoheihasegawa/you_inc/agent-core/tools/validate_sdd.py) | Audit | SDD要件トレーサビリティおよび品質ゲート完全性検証 |
| [`verify_loop_state.py`](file:///Users/shoheihasegawa/you_inc/agent-core/tools/verify_loop_state.py) | Audit | SDD/TDDループの各フェーズ（Outer Red, Green, Quality）の機械的判定 |
| [`audit_orphan_scripts.py`](file:///Users/shoheihasegawa/you_inc/agent-core/tools/audit_orphan_scripts.py) | Audit | どこからも参照されていない孤立スクリプトの監査検知 |
| [`pre_handoff_verify.sh`](file:///Users/shoheihasegawa/you_inc/agent-core/tools/pre_handoff_verify.sh) | Audit | コミット前の総合検証（テスト・Lint・SDD・孤立監査）の一括実行 |
| [`verify_cleanliness.py`](file:///Users/shoheihasegawa/you_inc/agent-core/tools/verify_cleanliness.py) | Audit | Agent OS の物理的クリーンネス（Leave No Trace, 行数制限）の機械的検証 |

> [!NOTE]
> 各ツールの詳細な引数やJSONスキーマ仕様は、各スクリプトの先頭 Docstring または `--help` 引数を参照せよ。
