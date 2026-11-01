# Agent-Core Tools (Catalog)

本ディレクトリは、Agentic OS で利用されるステートレスなCLIツールの格納場所である。  
設計思想・JSON-First Protocol・運用ルールについては [tool_design_principles.md](file:///Users/shoheihasegawa/you_inc/agent-core/docs/agent_rules/tool_design_principles.md) を参照せよ。

## 🛠️ ツール一覧 (Index)

| ツール名 | 種別 | 目的 (What / Why) |
| :--- | :--- | :--- |
| [`workspace_manager.py`](file:///Users/shoheihasegawa/you_inc/agent-core/tools/workspace_manager.py) | Harness | Epic Workspace および Git Worktree（`ws-new`, `ws-harvest`, `ws-list`）の管理 |
| [`audit_skills.py`](file:///Users/shoheihasegawa/you_inc/agent-core/tools/audit_skills.py) | Audit | `skills/` 配下の全 `SKILL.md` の構文・リンク整合性検証 |
| [`audit_orphan_scripts.py`](file:///Users/shoheihasegawa/you_inc/agent-core/tools/audit_orphan_scripts.py) | Audit | どこからも参照されていない孤立スクリプトの監査検知 |
| [`verify_cleanliness.py`](file:///Users/shoheihasegawa/you_inc/agent-core/tools/verify_cleanliness.py) | Audit | Agent OS の物理的クリーンネス（Leave No Trace, 行数制限）の機械的検証 |
| [`check_markdown_links.py`](file:///Users/shoheihasegawa/you_inc/agent-core/tools/check_markdown_links.py) | Audit | Markdown ファイル内の相対・絶対リンク切れ検証 |
| [`pre_handoff_verify.sh`](file:///Users/shoheihasegawa/you_inc/agent-core/tools/pre_handoff_verify.sh) | Audit | コミット前の総合検証（テスト・Lint・SDD・孤立監査）の一括実行 |

> [!NOTE]
> 各ツールの詳細な引数やJSONスキーマ仕様は、各スクリプトの先頭 Docstring または `--help` 引数を参照せよ。
