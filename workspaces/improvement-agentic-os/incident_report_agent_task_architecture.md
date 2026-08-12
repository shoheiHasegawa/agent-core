# インシデントレポート: agent_task モジュール実装時のアーキテクチャ逸脱

## 概要
Phase 5のTDD実装において、`core-service` の定めるアーキテクチャ規約（DDD, SOLID, テスト規約など）から著しく逸脱した実装が行われた。
このインシデントは、将来のAgentが同様の誤りを犯さないようにするための調査・反省材料として記録する。

## 発生した逸脱内容

### 1. DBアクセス技術の致命的矛盾 (ロック競合リスク)
- **あるべき姿**: `core-service` では `you_inc_ops.db` へのアクセスを `SQLAlchemy` の `Session`（UoWパターン）で統一し、DIコンテナ (`container.py`) から各リポジトリに注入している。
- **実装された姿**: 独自のピュアな `sqlite3` ドライバを用いた `SqliteAgentTaskRepository` を作成し、都度コネクションを生成する実装を行ってしまった。
- **リスク**: SQLAlchemyのトランザクションとピュアな sqlite3 のコネクションが同じ物理ファイルに同時アクセスしようとするため、「SQLite Database is locked」などのエラーが頻発し、システム全体がクラッシュする危険性が極めて高かった。さらにコネクションリークのバグも含まれていた。

### 2. インフラ層のパッケージング規約違反 (Package by Technology)
- **あるべき姿**: インフラ層 (`src/infrastructure/`) は、ドメイン名ではなく技術名（`sqlalchemy`, `local_file`, `google_api` 等）でパッケージを分割するルールがある。
- **実装された姿**: `infrastructure/agent_task/` というドメイン名のディレクトリを作成してしまった。

### 3. ファイル命名規則の不一致
- **あるべき姿**: ドメインオブジェクト名（ユビキタス言語）をそのままファイル名とする（例: `task.py`, `task_repository.py`）。
- **実装された姿**: システム的でジェネリックな `entity.py`, `repository.py` という命名にしてしまった。

### 4. テストの配置規約違反
- **あるべき姿**: `tests/unit/` (モック使用) と `tests/integration/` (実DB等へのアクセス) に分離する。
- **実装された姿**: トップレベルの `tests/application/agent_task/test_agent_task.py` に配置してしまった。

## 根本原因 (Root Cause)
Agentが実装を開始する際、対象リポジトリの全体的なアーキテクチャ方針 (`docs/architecture.md`, `docs/rules/ddd_guidelines.md`) や既存コード（`container.py` のDI構成など）のコンテキストを十分に確認せず、プロンプトの局所的な指示（「SQLiteを使う」「TDDを回す」）のみに過剰適合 (Overfitting) したため。
特に、「物理DBは `you_inc_ops.db` を共有する」という指示から「既存のSQLAlchemyエコシステムに乗る」という文脈を推論できず、独自にsqlite3で実装してしまった点が最大のエラーである。

## 今後の再発防止策
1. 新規ドメインの実装時は、必ず同リポジトリ内の既存ドメイン（例: `task_management`）のディレクトリ構成や実装パターンをリファレンスとして確認する。
2. `src/di/container.py` などの Composition Root を確認し、インフラ（DBセッション等）がどのように注入されているかを把握してから Repository を実装する。
3. `make check-all` に依存しすぎず、実行前にドキュメント（`docs/rules/*.md`）の設計規約と照らし合わせるセルフレビューを行う。
