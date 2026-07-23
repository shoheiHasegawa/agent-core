---
name: core-service-development
description: Use this skill when developing, refactoring, or testing features in the core-service repository. It contains strict rules for the Service-Config pattern and Dependency Injection.
---

# 🛡️ Core-Service Development Skill

## 1. 開発原則（SDD/TDD/DDD/SOLID/Context Engineering）の遵守
`core-service` リポジトリのすべての設計ルール、アーキテクチャ制約、およびコードレビュー基準は `core-service/docs/architecture.md` を起点とするドキュメント群（正本）に定義されています。
**[CRITICAL]** タスクの計画や実装を開始する前に、必ず `core-service/docs/architecture.md` およびそのリンク先（`rules/` 配下）を読み込み、これら5大原則の設計思想を理解した上で作業を行ってください。SKILLファイルに設計思想を直書きすることは禁止されています。

## 2. 実行環境とDIの制約
- **実行は `agent-core` へ**: 自身を実行するスクリプト（バッチやツール）は `core-service` に置かず、`agent-core` の `jobs/` または `tools/` に配置してください。
- `core-service` は純粋なドメインロジックの集合（ステートレス工場）です。環境変数や外部設定を内部で解決せず、必ず `agent-core` の `app_context.py` (Composition Root) から注入してください。

## 2. Service-Config パターン（依存性注入）
機密情報やパス情報は必ず「Service-Config」パターンを用いて外部から注入（DI）してください。
- `core-service` 側には、機能が必要とする設定の型（`dataclass`）のみを定義します。
- `agent-core` 側の `app_context.py`（Composition Root）内で、実際の設定ファイル（`.env` 等）を読み込んで Config インスタンスを組み立て、`core-service` の `CoreServiceContainer` を初期化します。
  - ⚠️ **[CRITICAL] DIコンテナの外部呼び出し**: 旧来の `factories/` ラッパーは廃止されました。実行スクリプトからは `from app_context import get_core_service_container` を呼び出して Service を取得してください。

## 3. アーキテクチャ命名規則（Naming Conventions）
ドメイン層とインフラ層の関心事を分離し、AIのハルシネーション（エイリアス等）を防ぐため、以下の命名規則を厳守してください。
- **Interface Naming Rule (Domain層)**: インターフェース名はドメイン概念をそのまま表す名称（例: `TaskRepository`, `IssueParser`）を使用してください。C#やJavaに見られるようなインターフェース特有の接頭辞（例: `ITaskRepository`）を付与してはなりません。
- **Implementation Naming Rule (Infrastructure層)**: 実装クラスには必ず技術的詳細を示す接頭辞を冠してください（例: `SqlTaskRepository`, `LocalFileMobileVaultRepository`）。インターフェースと同名にすることは（importエイリアスが必要になるため）厳禁です。

## 4. リソース管理のベストプラクティス（DBセッション等）
エントリポイント（バッチスクリプトやCLIツール）等においてデータベースのセッションを生成・管理する際は、必ず `with SessionLocal() as session:` のようにコンテキストマネージャー（with 句）を使用し、異常時にも確実にリソースが解放される堅牢な設計（PEP 343準拠）を標準方針としてください。`try-finally` によるレガシーな手動クローズ管理は禁止とします。

## 5. Gateway パターンの標準化 (外部システム連携)
DDDの厳格な責務分離に基づき、インターフェースの使い分けを以下のように標準化します。
- **Repository**: ドメインオブジェクト（Aggregate）のDB永続化や復元にのみ使用すること。
- **Gateway**: 外部システム（API、Event Bus、Queue、OS通知など）への単方向通信や連携には、必ず `Gateway` という名称を用いたPort（インターフェース）を定義して使用すること（例: `SystemEventGateway`）。
  - さらに責務を細分化する場合、`Publisher`, `Reader`, `Receiver` などの粒度の細かいユビキタス言語をPort名として使用することも推奨します。
  - エラーハンドリングやログ出力などのシステムイベントを発行する際も、必ずこのGateway経由でQueueにパケットとして投函（Publish）すること。独自のログファイル出力処理を実装することはアーキテクチャ違反とする。

## 6. Application 層と Composition Root の設計原則
- **Facade と UseCase の分離**: Application層では、すべての処理を1つのクラスに詰め込む「ファットサービス」を禁止します。入り口として Facade パターン (`~Service`) を配置し、外の世界に対してはシンプルでわかりやすいAPIを提供してください。その上で、実際の複雑なビジネスロジックはSRP（単一責任の原則）に基づく個別の `~UseCase` クラスに委譲する設計を標準とします。
- **Composition Root (DI)**: インフラの実装とUseCaseを結合し、Serviceを組み立てる依存性注入（DI）のロジックは、Application層の内部に置いてはいけません（インフラへの依存逆流を防ぐため）。必ず `core-service/src/di/` というトップレベルのディレクトリ（Composition Root）に配置し、`agent-core` などのコンシューマーに組み立て済みの Service インスタンスを提供する SDK 的な責務を持たせてください。

## 7. テストとコンプライアンスチェッカー (`validate_sdd.py`) の遵守事項
`core-service` のテストは `validate_sdd.py` によって厳格に監視されます。以下のルールを厳守してください。
- **配置の厳格化**: `@patch` や `MagicMock` を使用するテストは「Unitテスト」とみなし、必ず `tests/unit/` 配下に配置してください。DBや外部システムへの実際の結合をテストするものは `tests/integration/` に配置します。
- **Empty Assertion 検知への対応**: `validate_sdd.py` は、テストコード内にネイティブな `assert` キーワードが存在するかを字句レベルで検査します。`mock.assert_called_once()` などのモックアサーションメソッドを呼んでいる場合でも、スクリプトを通すために必ず `assert mock.called` あるいは `assert True` のようなネイティブな `assert` 文を含める必要があります。
- **Fake Mocking 禁止**: `MagicMock` や `@patch` を使用する際は、シグネチャの不一致による偽陽性を防ぐため、必ず `autospec=True` または `spec=True` を付与してください。
