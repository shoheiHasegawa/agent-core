# Agent-Core Tools (Catalog)

本ディレクトリは、`agent-core`（本社リポジトリ）のWorktreeハーネスおよび静的品質ゲート（Linter）スクリプトの格納場所である。
（※業務ドメイン用の公式CLIツールはすべて `core-service/src/entrypoints/cli/` 側に集約されている。設計境界の詳細は [`docs/architecture.md`](../docs/architecture.md) を参照せよ。）

## 🛠️ ツール一覧 (Index)

| ツール名 | 種別 | 目的 (What / Why) |
| :--- | :--- | :--- |
| [`workspace_manager.py`](workspace_manager.py) | Harness | Epic Workspace および Git Worktree（`ws-new`, `ws-harvest`, `ws-list`）の管理 |
| [`sandbox_runner.py`](sandbox_runner.py) | Security Harness | macOS `sandbox-exec`（[`config/sandbox/worker.sb`](../config/sandbox/worker.sb)）によるロール別最小権限（`--role {leader,worker,reviewer}`, `--allow-net`）実行ラッパーおよび決定論的自己検証（`--self-test`）。詳細は [`docs/specs/makefile_seatbelt_spec.md`](../docs/specs/makefile_seatbelt_spec.md) を参照。 |
| [`authenticate_google.py`](authenticate_google.py) | Auth | Google Tasks & Calendar API の初回 OAuth 2.0 認可ワンショットスクリプト |
| [`audit_skills.py`](audit_skills.py) | Audit | `skills/` 配下の全 `SKILL.md` の構文・リンク整合性検証 |
| [`audit_orphan_scripts.py`](audit_orphan_scripts.py) | Audit | どこからも参照されていない孤立スクリプト・テンプレートの監査検知 |
| [`verify_cleanliness.py`](verify_cleanliness.py) | Audit | Agent OS の物理的クリーンネス（Leave No Trace, `context.md` 行数制限）の機械的検証 |
| [`check_markdown_links.py`](check_markdown_links.py) | Audit | Markdown ファイル内の相対・絶対リンク切れ検証 |
| [`pre_handoff_verify.sh`](pre_handoff_verify.sh) | Hook Gate | Git `pre-commit` フックから呼び出される物理検証エントリポイント（`make check-all` を実行し違反時にコミットを即ブロック） |

> [!NOTE]
> 各ツールの詳細な引数は、各スクリプトの先頭 Docstring または `--help` 引数を参照せよ。
