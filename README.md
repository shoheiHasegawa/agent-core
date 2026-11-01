# 🏢 agent-core (You_Inc Headquarters)

`agent-core` は、You_Inc（「社長 ⇄ 秘書 ⇄ チームリーダー ⇄ メンバー」で稼働する自律型Agent会社）の**本社・司令塔リポジトリ**です。
全社の憲法・思考原則・経験ストック・SKILL定義・環境設定（Config/Secret）、および各プロジェクト（Epic）の隔離ワークスペースを管理します。

---

## 📂 ディレクトリ構造マップ

| パス | 役割・内容 |
| :--- | :--- |
| [`GEMINI.md`](GEMINI.md) | **Layer 1（全社憲法）**: 全リポジトリ・全Agentが遵守する最上位原則 |
| [`AGENTS.md`](AGENTS.md) | **Layer 2（本社コンテキスト）**: 秘書（`executive-secretary`）の起動と4層組織・3層知識のルーティング |
| `config/` | 環境設定（`conf.env`）および SOPS 暗号化された機密情報（`secret.env`）の保管庫 |
| `docs/system/` | You_Inc 全体のシステム構成・アーキテクチャ設計ドキュメント |
| `docs/agent_rules/` | **思考のOS（原則）**: DDD/SOLID/YAGNI、引き算ファースト、2-Pass スパイラルループ等の判断基準 |
| `docs/experiences/` | **経験ストック（学び）**: 現場で起きた失敗パターン・アンチパターン・過去の社長判断（前例）の蓄積 |
| `docs/templates/` | `spec_template.md` 等の標準ドキュメントテンプレート |
| `skills/` | **薄いSKILL群**: 秘書・チームリーダー・TDDワーカー・独立レビュアー・知識蒸留の入出力契約と停止条件 |
| `tools/` | Worktree管理（[`workspace_manager.py`](tools/workspace_manager.py)）およびリポジトリ品質ゲート用Linter群 |
| `workspaces/` | Epic単位の作業空間。内部の `worktrees/<repo>/`（`.gitignore` 対象）に各リポジトリのブランチをマウントして隔離開発を行う |
| `backlog/` | 長期構想・バックログメモの保管庫（日常の課題管理は GitHub Issues を正本とする） |
| `scratch/` | 一時ファイル用サンドボックス（作業完了時に破棄） |

---

## 🛠️ 主要コマンド (`Makefile`)

```bash
# 1. 新規Epicワークスペースの立ち上げとWorktreeマウント (branch: epic/<name>)
make ws-new EPIC=<name> REPOS=core-service,agent-core ISSUE=<github_issue_num>

# 2. アクティブなワークスペースとマウント中のWorktree一覧表示
make ws-list

# 3. Epic完了時のWorktreeアンマウントと一時ファイル掃除（PR回収準備）
make ws-harvest EPIC=<name>

# 4. 本社リポジトリの品質ゲート一括実行（SKILL構文・クリーンネス・孤立スクリプト・リンク検証）
make check-all
```
