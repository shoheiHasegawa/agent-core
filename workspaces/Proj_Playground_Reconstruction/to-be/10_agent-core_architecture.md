# 10_agent-core アーキテクチャ設計書

## 1. 概要と責務
`agent-core` は、Agentたちが存在し、タスクを処理し、成長する「本社・拠点」となるリポジトリである。
システム全体の実行状態（ステート）と、外部とのI/O（副作用）をすべてこのリポジトリに封じ込める。

## 2. ディレクトリ構成
```text
agent-core/
├── README.md            # [人間向け・ルーター] リポジトリの目的と全体像
├── GEMINI.md            # [AI向け・起点] 絶対ルールと各ディレクトリへのポインタ(JITロード起点)
├── INDEX.md             # [オンデマンド] 詳細なディレクトリマップ（地図）
├── AGENT.md             # プロジェクト全体の絶対ルール・指針
├── agents/              # [SSOT] 各Agent（CEO, COO等）のシステムプロンプト・ペルソナ定義の実体
├── skills/              # Agentの能力・ドメイン知識のパッケージ
├── actions/             # [薄いラッパー] core-service(情報システム部)等のAPIを叩くための接着剤・スクリプト
├── workflows/           # タスクの処理手順（ルーティング・パイプライン）
├── epics/               # 巨大なプロジェクトの全体像・バックログ
├── queue/               # Agentへのタスク指示（Issue）のキュー
├── templates/           # [追加] agent-coreで利用する動的テンプレート群 (進捗ログ、PRフォーマット等)
├── workspaces/          # 隔離作業環境（git worktree / Dockerマウント用）
│   ├── active/          # 実行中の作業場
│   └── archived/        # [追加] 作業完了後、Harvest抽出・人間承認待ちの一時凍結領域（Grace Period）
└── config/              # 環境変数、シークレット（core-serviceへDIされる）用
```

## 3. コア機能とルール

### 3.1 Skill と Workflow の分離
- **Skill**: 単一の責務を持つ能力の定義。例えば「DDD実装スキル」「Chrome Extension開発スキル」など。必要なツール（actions）のリストと、処理のためのコンテキスト（知識）を内包する。
- **Workflow**: タスクの目的に応じて、どのSkillをロードし、どの順序で実行するかを定義するルーティング・パイプライン。

### 3.2 隔離作業場（git worktree & Docker）と適応型PRガバナンス
Agentが誤ってメインブランチや他のプロジェクトを破壊するのを防ぐため、**「論理と物理の隔離（ハーネス）」**を徹底する。
- **論理的隔離**: `workspaces/` ディレクトリ配下では、対象プロジェクトのリポジトリを `git worktree` を用いて別ブランチとして展開する。
- **物理的隔離 (使い捨てサンドボックス)**: Agentが未知のコードを実行する際は、ホストOSではなく公式の汎用イメージ（`python:3.x-slim`等）を `docker run --rm` で呼び出し、マウント領域を `workspaces/` に限定して実行する。カスタムDockerfileは不要とし、タスクごとに使い捨てる。
- 作業完了後は必ず Pull Request (PR) を作成する。

### 3.3 コアルールの保護と社長承認の必須化
`AGENT.md` や `GEMINI.md` といったシステム全体のコアルールは、Agent単独での変更マージを禁止する。これらのファイルに対するPRは、必ず人間（社長）の最終承認を必須とするガバナンスを設ける。

### 3.4 依存性注入 (DI) の実行主体
`core-service` にはシークレットや環境変数を持たせず、`agent-core` 側が `sops` 等を用いて暗号化管理（`.env.sops` 等）する。
実行時に `agent-core` がそれを復号し、`pyproject.toml` 等でローカルパス参照した `core-service` のライブラリ群に対して注入（DI）する責務を持つ。

### 3.5 自己記述型（Self-Describing）の徹底とコンテキスト起点の固定
「各ディレクトリに何を置いていいか（責務）」をAgentに守らせるため、以下の仕組みを導入する。
1. **コンテキスト起点の固定**: Agentはタスク開始時、無条件にルートの `GEMINI.md` と `README.md` を読み込む。ここには「システムの設定ルールは `second-brain/90_Meta/System_Rules/` を見よ」といったポインタがハードコードされており、Agentが迷子になること（ブートストラップの罠）を防ぐ。
2. **自己記述のミニマム要件 (Colocation)**: `agents/` や `workflows/` などの各ディレクトリ内には、必ず `_index.md`（またはREADME）を置き、「このディレクトリの責務」を1行で自己記述させる。ドキュメントを別ディレクトリに隔離しないことで仕様のドリフトを防ぐ。
3. **JITロード（遅延ロード）**: `GEMINI.md` のポインタに従い、自身のタスクに関連する詳細ルール**だけ**をピンポイントで遅延ロード（Lazy Loading）する。

### 3.6 テンプレートの定義と利用
Agentのシステム的な実行状態（Compute/State）を保持・通知するため、`agent-core/templates/` に以下のフォーマット群を強制する。これらは `second-brain` 側のナレッジとは異なり、システムの一時的かつ動的なログやフォーマットである。
1. `Workspace_Progress_Template.md`: `workspaces/active/` 内で日々の進捗とNext Actionを管理する型。
2. `Decision_Log_Template.md`: `workspaces/active/decisions.md` として、失敗録（Why NOT）を残す型。
3. `Harvest_Report_Template.md`: Workspace完了後に出力する教訓・技術的負債のレポート型。
4. `Agent_Persona_Template.md`: `agents/` 配下のRoleやSystem Promptの定義型。
5. `Proposal_Approval_Template.md`: 破壊的変更前に人間にPR承認を求めるための安全フォーマット。
6. `Incident_Recovery_Template.md`: Agentのエラー時や暴走からの復旧手順を残すPost Mortem用。
