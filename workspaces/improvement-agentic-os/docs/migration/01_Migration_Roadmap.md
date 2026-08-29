# Agentic OS マイグレーション・ロードマップ

本ドキュメントは、AS-ISの課題（セキュリティリスク、Agentへの過度な依存、状態管理の破綻等）を解消し、TO-BEアーキテクチャ（Thin Orchestrator + PubSub, Task Registry）へ移行するための具体的な実装計画である。

## Step 0: Security Patch (データ隔離と漏洩防止)
システム全体の堅牢性を担保するため、まずは既存の永続化リスクとクレデンシャル流出の穴を塞ぐ。

*   **対象ファイル:** `agent-core/.gitignore`
    *   **変更内容:** 
        *   `!events/handoff_*.md` の記述を削除し、ハンドオフ時のセッションログがGitに追跡されないようにする。
        *   `tasks/progress.md` および `tasks/context.md` を追加し、ワークスペースの作業状態ファイルが誤ってGit履歴に混入するのを防ぐ。
*   **対象ファイル:** `agent-core/tools/verify_cleanliness.py`
    *   **変更内容:** `exclude_dirs` （64行目付近）から `scratch/` を削除する。もしくは、チェック処理を追加し、`scratch/` ディレクトリ内に一時ファイルや機密データが残存していないかを終了時に厳格に検証（空であることの確認）するようロジックを修正する。
*   **対象ファイル:** `agent-core/skills/session-manager/SKILL.md`
    *   **変更内容:** 終了シーケンス（Handoff）における盲目的な `git add . && git commit -m ...` の指示を削除する。代わりに、「必ず `git status` と `git diff` を実行して機密情報が含まれていないか確認してから、意図したファイルのみをステージングしてコミットする」という厳格な手順（Interactive Prompting または Strict Filtering）に書き換える。

## Step 1: Rule Reduction (ルール引き算と認知負荷の削減)
Agentに対するSoft Constraints（プロンプトでの指示）を大幅に削減し、システム側（Hard Constraints）への移譲準備を行う。

*   **対象ファイル:** `agent-core/AGENT.md`
    *   **変更内容:**
        *   `<jit_routing>` セクションを削除、または大幅に縮小する（ルールの事前読み込みはOrchestratorやOS側が自動注入する設計となるため）。
        *   `<progress_tracking>` の手動更新（`progress.md` のチェックボックス管理）に関するルールを削除する（Task Registryへ移行するため）。
        *   `<governance>` の多重レビューオーケストレーション（Agent自身がレビューツールを呼び出す手順）を削除し、CIパイプラインやPubSub側のイベントハンドラに責務を移譲するよう文面を整理する。
*   **対象ファイル:** 各リポジトリの `AGENT.md` (`second-brain/AGENT.md`, `core-service/AGENT.md`)
    *   **変更内容:** 全体ルールと重複している記述を削除し、当該リポジトリ特有のローカルルール（特定のエコシステムや配置ルール）のみに純化させる。

## Step 2: Gatekeeper Hardening (堅牢な実行環境とエラー監視)
Agentのクラッシュによるサイレントデッドロックを防ぎ、ツールの入力バリデーションを厳格化する。

*   **対象ファイル (新規作成):** `core-service/src/domain/system/supervisor.py` (または同等の実行基盤)
    *   **変更内容:** Agentの実行（`invoke_subagent` やツールの実行）をラップする `LifecycleSupervisor` クラスを新設。Watchdogタイマー（一定時間応答がない場合のタイムアウト検知）と、未処理例外（OOMやクラッシュ）をキャッチしてOrchestratorに代理でエラーイベントを発行するフェイルセーフロジックを実装する。
*   **対象ファイル:** `agent-core/tools/` 配下の各ツール（例: `process_inbox_item.py` 等）
    *   **変更内容:** 実行前に必ず厳密なJSON SchemaまたはPydanticモデルによる事前バリデーションを挟む。バリデーションエラー時には処理を落とさず、"Field X is missing / wrong type" などの具体的な修正指示（Actionable Feedback）をAgentのコンテキストに直接返却する構造にリファクタリングする。
    *   標準出力・標準エラー出力の切り捨て（Truncation）をやめ、上限を超える場合はアーティファクトファイルへの自動ダンプとパスの返却を行う仕組みを導入する。

## Step 3: State/PubSub Migration (状態管理と非同期ループへの移行)
脆いファイルベース（Markdown）の進捗管理を廃止し、ACIDトランザクションをサポートするSQLite Task RegistryとPubSub機構へ移行する。

*   **対象ファイル (新規作成):** `core-service/src/infrastructure/database/migrations/xxxx_create_tasks_table.sql`
    *   **変更内容:** TO-BE仕様に基づき、タスクID、タイトル、ステータス (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `FAILED`)、`assigned_to`、`locked_at` を持つ `tasks` テーブルのDDLを作成する。
*   **対象ファイル (新規作成):** `core-service/src/domain/task_registry/task_repository.py`
    *   **変更内容:** `UPDATE tasks SET status = 'IN_PROGRESS' ... WHERE id = ? AND status = 'PENDING'` を用いたAtomicなチェックアウト処理、およびタイムアウトしたタスクのリカバリ（`locked_at` 超過タスクのPENDING差し戻し）ロジックを実装する。
*   **対象ファイル:** `agent-core/workspaces/**/tasks/progress.md` および `context.md`
    *   **変更内容:** 当該ファイル群を削除・廃止。進行中のタスクデータは全てSQLite（Task Registry）へ移行する。
*   **対象ファイル:** `agent-core/skills/session-manager/SKILL.md`
    *   **変更内容:** 起動シーケンスを、「`progress.md` を読み込む」手順から、「Task API (Task Registry) から `PENDING` または `IN_PROGRESS` のタスクをフェッチして再開する」フローへ書き換える。
