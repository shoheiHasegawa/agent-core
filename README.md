# 🏢 agent-core (You_Inc Headquarters)

## 🎯 本リポジトリの存在目的 (WHY)
`agent-core` は、You_Inc（「社長 ⇄ 秘書 ⇄ チームリーダー ⇄ メンバー」で稼働する自律型Agent会社）の**本社・司令塔リポジトリ**です。
ビジネスロジックや定型機械処理（`core-service`）および社長個人の知識資産（`second-brain`）から独立し、**「全社の憲法・思考原則・経験ストック・SKILL契約・環境設定（Config/Secret）・隔離Worktreeハーネス」を一元統括して自律チームの学習と実行を制御するため**に存在します。

---

## 📂 WHAT：ディレクトリ構造マップ

| パス | 役割・内容（WHY / WHAT） |
| :--- | :--- |
| [`GEMINI.md`](GEMINI.md) | **Layer 1（全社憲法）**: 全リポジトリ・全Agentが遵守する最上位の目的（WHY）と絶対境界 |
| [`AGENTS.md`](AGENTS.md) | **Layer 2（本社コンテキスト）**: 秘書（`executive-secretary`）の起動と4層組織・3層知識のルーティング |
| [`docs/architecture.md`](docs/architecture.md) | **全社アーキテクチャ設計書 (Timeless SSOT)**: 会社の現在地の俯瞰と、将来のカイゼン時のベースラインとなる設計正本 |
| [`docs/rules/`](docs/rules/thinking_os_and_loop_principles.md) | **Layer B（思考のOS）**: `WHY ➔ WHAT ➔ HOW`、引き算ファースト、DDD/SOLID、2-Passループ、Zettelkasten 対話原則 |
| [`docs/experiences/`](docs/experiences/README.md) | **Layer C（経験・前例ストック）**: 現場で起きた失敗パターン（`[EXP-XX]`）と過去の社長判断・前例（`[PREC-XX]`）の蓄積 |
| [`docs/templates/`](docs/templates/spec_template.md) | `spec_template.md`（SDD 6大観点の仕様テンプレート） |
| [`skills/`](skills/README.md) | **Layer A（薄いSKILL群）**: 秘書・チームリーダー・TDDワーカー・独立レビュアー・知識蒸留の7コアスキル |
| [`tools/`](tools/README.md) | Worktree管理（[`workspace_manager.py`](tools/workspace_manager.py)）およびリポジトリ品質ゲート用Linter群 |
| `config/` | 環境設定（`conf.env`）および SOPS 暗号化された機密情報（`secret.env`）の保管庫 |
| `workspaces/` | Epic単位の作業空間。内部の `worktrees/<repo>/`（`.gitignore` 対象）に各リポジトリのブランチをマウントして隔離開発を行う |
| `backlog/` | 長期構想・バックログメモの保管庫（日常の課題管理は GitHub Issues を正本とする） |
| `scratch/` | 一時ファイル用サンドボックス（作業完了時に破棄） |

---

## 🛠️ HOW：主要コマンド (`Makefile`)

```bash
# 1. 新規Epicワークスペースの立ち上げとWorktreeマウント (branch: epic/<name>)
make ws-new EPIC=<name> REPOS=core-service,agent-core ISSUE=<github_issue_num>

# 2. アクティブなワークスペースとマウント中のWorktree一覧表示
make ws-list

# 3. Epic完了時のWorktreeアンマウントと一時ファイル掃除（PR回収準備）
make ws-harvest EPIC=<name>

# 4. core-service 公式CLIの実行（Zettelkasten 監査・Mobile Vault 確認）
make zk-audit
make vault-peek

# 5. 本社リポジトリの品質ゲート一括実行（SKILL構文・クリーンネス・孤立スクリプト・リンク検証）
make check-all
```
