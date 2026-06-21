---
status: icebox
created: "2026-06-21"
---

# Epic 04: Agentic OS Harness Construction

## 概要
移行プロジェクト（Proj_Playground_Reconstruction）にて「リポジトリ構造の分離とデータの移行」は完了したが、TO-BEアーキテクチャで描かれた「Agentが自律的かつ安全に自動運転するためのインフラ（Harness）」は未実装である。
本エピックは、将来的にAgentの完全自律稼働（自動運転）を開始する際に着手すべき「安全装置・自動化インフラ」の構築タスクを保管するバックログである。

## 背景と課題（2026年6月 システム監査より）
1. **ルールの暗黙知化**: TO-BE設計書（ADR）で定めた「権限ルールの差異」や「YAMLのフェールセーフ機構（requires_human）」が、`GEMINI.md` や実際のテンプレートにハードコードされていない。
2. **物理ハーネスの不在**: `make workspace` による作業領域の隔離や、Dockerコンテナ内での `git worktree` マウントといった物理的なサンドボックス環境が存在しない。
3. **自動制御の不在**: `queue/` を処理する非同期ロジック、タスクのWIP制限、CI/CDのpre-commitフック、サーキットブレーカー（エラー時の暴走停止機構）が未実装。

---

## 📝 バックログ（Future Tasks）

### 1. 憲法・ガバナンスのコード化 (Codify Rules)
- [ ] `GEMINI.md` にリポジトリごとのPush権限（agent-coreはPR必須、second-brainはDirect Push可）を明記する。
- [ ] `AGENT.md` に「新規機能ディレクトリ作成時の `_index.md` 配置義務（自己記述要件）」を追記する。
- [ ] `Permanent_Note.md` 等の全Zettelkastenテンプレートに `requires_human: true/false` フラグを追加し、人間へのエスカレーション判定を強制する。

### 2. 物理ハーネスとサンドボックスの構築 (Physical Harness)
- [ ] `agent-core` 内で安全にコードを実行・テストするための `docker-compose.yml` および `Dockerfile` （使い捨て環境）の作成。
- [ ] 作業領域（Workspace）を自動生成し、WIP上限を制御するための `make workspace` コマンドの実装。
- [ ] コンテナ内で `git worktree` をマウントし、ホスト環境を汚染せずに隔離実行する仕組みの構築。

### 3. 自動運転・ストッパー機構の構築 (Automation & Breakers)
- [ ] `queue/` フォルダのタスクを非同期で順番に拾い、並列実行を制御するキュープロセッサの実装。
- [ ] Gitのコミット前にフォーマットや禁止事項を自動チェックする `pre-commit` フックの整備。
- [ ] Agentが無限修正ループに陥るのを防ぐため、「3回失敗したら社長（人間）にメンションして停止する」サーキットブレーカーロジックの実装。
- [ ] 作業終了後の不要なコンテナ・ディレクトリの自動破棄と、`Harvest_Report` の自動抽出を行うGarbage Collectionスクリプトの実装。

### 4. コンテキスト維持と進捗管理 (Progress Tracking)
- [ ] LLMの記憶喪失（コンテキストウィンドウ枯渇）を防ぐため、タスク着手時・完了時に必ずワークスペース内の `progress.md` を更新させる運用ルールを `AGENT.md` に明記する。


### 📥 追加システム要件（旧体制からの引き継ぎ）
- **Agent間連携プロトコル等**: # 💡 AgentOS Expansion Backlog (次期フェーズ拡張案)  本プロジェクト（AgentOS Upgrade）の範囲外として整理された、将来的な拡張アイデアのリストです。  ## ⚙️ 役員室の高度化 (Executive Automation) - **COO: プロジェク...
- **メール認証セキュリティ(Bot専用)**: --- title: "[Infrastructure] 個人の自動化ボットにおけるメール認証アーキテクチャ" date: "2026-04-20" tags: ["infrastructure", "security", "todo"] ---  # 概要 `Mail_Content_Conver...
- **ReviewWatcherのZettelkasten統合**: # Idea: Review Watcher Zettelkasten Integration  ## 概要 現在、`review_watcher` は AgentOS の教訓（`AGENTS.md` / `personas/*.md`）の自己成長ループに特化して稼働している。 しかし、当初の構想（...
