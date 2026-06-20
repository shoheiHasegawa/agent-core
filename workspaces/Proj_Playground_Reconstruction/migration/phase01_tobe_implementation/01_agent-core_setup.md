# Phase01: agent-core 初期実装タスク

## 1. 目標
システム全体の実行状態と外部I/Oの副作用を封じ込める、Agentの「本社・拠点」のスケルトンを構築し、MVPとして稼働可能にする。

## 2. ディレクトリ構造の作成
以下のディレクトリを初期作成する。
- `agents/` (SSOT: Agentペルソナ)
- `skills/` (ドメイン知識パッケージ)
- `actions/` (外部I/O用ラッパー)
- `workflows/` (ルーティング・パイプライン)
- `epics/` (プロジェクトバックログ)
- `queue/` (タスク指示のキュー)
- `templates/` (動的テンプレート群)
- `workspaces/active/` (実行中の隔離作業環境)
- `workspaces/archived/` (作業完了後の一時凍結領域)
- `config/` (core-serviceへのDI用)

## 3. 必須ファイルの作成
### 3.1. ルート・自己記述ファイル
- `README.md` (目的と全体像)
- `GEMINI.md` (絶対ルールとJITロード起点のポインタ)
- `INDEX.md` (詳細ディレクトリマップ)
- `AGENT.md` (プロジェクト全体の絶対ルール・指針)
- 各ディレクトリ（`agents/`, `workflows/`等）直下に `_index.md` (自己記述ミニマム要件) を配置

### 3.2. テンプレートファイル群 (`templates/` 配下)
- `Workspace_Progress_Template.md`
- `Decision_Log_Template.md`
- `Harvest_Report_Template.md`
- `Agent_Persona_Template.md`
- `Proposal_Approval_Template.md`
- `Incident_Recovery_Template.md`

### 2. `You_Inc` ルートと `agent-core` のリポジトリ作成
- [ ] `play_ground/` 直下に `You_Inc` ルートディレクトリを作成し、その配下に `agent-core` のリポジトリを初期化する。
```bash
set -e
cd /Users/shoheihasegawa/play_ground
mkdir -p You_Inc
cd You_Inc
mkdir -p agent-core
cd agent-core
git init
git remote add origin <agent-core-remote-url> # URLは要確認
```

## 4. 基盤コード・仕組みの実装要件
- **隔離作業環境の枠組み**: `workspaces/active/` 領域を用いた git worktree のマウント設計。
- **Dockerコンテナ隔離**: Agentが未知のコードを実行する際のみ、公式の汎用イメージ（`python:3.x-slim`等）を `docker run --rm` で使い捨てサンドボックスとして呼び出す（カスタムDockerfileは不要）。
- **クレデンシャルDIと連携準備**: `life-automation` を踏襲し、`sops` で暗号化された `.env` ファイルを復号して実行時に渡す。また、`core-service` を `pyproject.toml` 等でローカルパスとして指定し、DIする構成とする。
- **PRガバナンス**: `AGENT.md` や `GEMINI.md` 等コアルールへのAgent単独変更をブロックし、社長（人間）の最終承認を必須化するルールの整備。
