# 調査報告: 非同期PubSub化に向けた堅牢なタスクレジストリ（State管理）アーキテクチャ

## 1. 背景と課題 (Problem Statement)
Agentic OSにおいて「Thin Orchestrator / PubSub」による非同期メッセージングモデルへ移行するにあたり、既存のMarkdownベース（`progress.md`等）によるステート管理は致命的な脆弱性を抱えている。
複数のエージェントやバックグラウンドタスクが同時にファイルへ書き込みを行うことで、以下の問題が発生する。
- **競合破壊 (Race Conditions):** 複数プロセスの同時更新によるファイルの破損、一部更新の消失。
- **Amnesia リスク:** 状態の一部が上書きされることで、エージェントが過去の文脈や進行状況を喪失し、無限ループやタスクの重複実行を引き起こすリスク。

## 2. 提案アーキテクチャ: 堅牢なタスクレジストリ (State API / DB)
Markdownファイルによる直接管理を廃止し、排他制御とトランザクションを担保する専用のデータベース（SQLite等）と、それをラップするState APIを導入する。

### 2.1 アーキテクチャ概要
1. **データベース層:** 組み込み容易かつファイルベースで管理できる SQLite、あるいは専用の KVS/RDB を採用。
2. **State API (ミドルウェア層):** エージェントは直接DBを触らず、標準化されたAPI（gRPC/REST/ローカルIPC）を経由して状態の取得・更新（State Mutation）を行う。
3. **PubSub連携:** 状態が更新された際、API層から自動的にPubSubのイベント（`task.updated`, `task.completed`等）を発火し、サブスクライバ（オーケストレータや他のエージェント）へ通知する。

## 3. スキーマ設計案 (Schema Design)
タスクとその実行ログ、依存関係を管理するための基本設計。

### Table: `Tasks`
- `id` (UUID): タスクの一意な識別子
- `parent_id` (UUID, nullable): 親タスクID（サブタスクの場合）
- `name` (String): タスク名
- `status` (Enum): `PENDING`, `IN_PROGRESS`, `BLOCKED`, `COMPLETED`, `FAILED`
- `assigned_agent` (String): 担当エージェントID
- `context` (JSON): タスク実行に必要な文脈情報やパラメータ
- `created_at`, `updated_at` (Timestamp)

### Table: `TaskEvents` (Event Sourcing用 / ログ)
- `id` (UUID)
- `task_id` (UUID): 関連するタスクID
- `event_type` (String): `STATUS_CHANGED`, `LOG_APPENDED`, `ERROR_OCCURRED` 等
- `payload` (JSON): 変更内容やログメッセージ詳細
- `timestamp` (Timestamp)

## 4. MUSTレベルの移行要件 (Technical Requirements)

1. **ACIDトランザクションと排他制御の徹底**
   - 複数エージェントからの同時更新を防ぐため、行レベルのロック（Row-level locking）または楽観的並行性制御（Optimistic Concurrency Control, ex: 世代管理）を実装すること。
2. **State APIの強制使用 (Direct File Accessの禁止)**
   - 全てのエージェントのツールから `progress.md` などの直接編集を禁止・削除し、代わりに `update_task_state` といったAPIツール経由でのみ状態変更を許可する。
3. **イベント駆動の同期**
   - 状態更新時は必ずイベントが発火し、ポーリングなしに状態変化を他エージェントが検知できる仕組みにすること。
4. **可逆性と監査性 (Auditability)**
   - 状態の上書きによるAmnesiaを防ぐため、状態変更は必ず `TaskEvents` テーブルに追記型（Append-only）で履歴を残すこと。

## 5. 潜在的な移行ブロッカーと対策 (Transition Blockers & Mitigation)
- **ブロッカー1: 既存プロンプト・ツールの依存**
  - エージェントのプロンプトが「progress.mdを読め」と強く指示されている場合、DB移行時に混乱を招く。
  - *対策:* LLMに対するシステムプロンプトを一斉更新し、状態把握用の参照ツール（`get_task_status`等）を新規提供する。
- **ブロッカー2: 状態の可視化ダウンタイム**
  - Markdownファイルは人間（ユーザー）にとっても直接読めるというメリットがあった。DB化すると中身が見えなくなる。
  - *対策:* UI/CLIツール、またはDBからリアルタイムに読み取り専用の `progress_view.md` を自動生成（エクスポート）するリードレプリカ的なワーカーを配置する。
