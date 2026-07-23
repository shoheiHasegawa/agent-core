# Orchestration Rules (Jobs, Tools & Factories)

`agent-core` はシステム全体を統括する司令塔であり、運用層です。`core-service`（ステートレスなドメインロジック）を呼び出して実行する際は、以下の構成とルールに従ってください。

## 1. Composition Root (`app_context.py`)
`core-service` の Service は、環境変数や設定を一切持ちません。依存関係の解決は `core-service/src/di/container.py` に集約されています。
`agent-core` では、`agent-core/app_context.py` がシステムの **Composition Root** として機能し、`agent-core/config/` 等から環境変数を読み込んで `core-service` の DI コンテナを初期化します。

各ジョブやツールは、必ず `from app_context import get_core_service_container` を用いて、構築済みの DI コンテナから Service インスタンスを取得（DI）してください。旧来の `factories/` ディレクトリを用いたラッパーパターンは完全に廃止されました。

### 🚫 ハードコードの完全禁止 (No Hardcoding Rule)
`app_context.py` や各種実行スクリプト内に、パスやディレクトリ名、APIキー等を**直書き（ハードコード）してはなりません**。
必ず `agent-core/config/conf.env` などの設定ファイルや環境変数から動的に値をパースし、設定変更時にコードの改修が不要な状態を保ってください。

## 2. 実行の入り口 (`jobs/` と `tools/`)
構築済みの DI コンテナから取得した Service は、以下の用途に応じて適切なディレクトリから呼び出してください。
- **`jobs/`**: 定期実行バッチ、深夜処理、`launchd` 等から直列で呼び出される自動化スクリプト。
- **`tools/`**: Agent が能動的に利用する検証ツールやユーティリティスクリプト。
