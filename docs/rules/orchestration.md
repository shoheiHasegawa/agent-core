# Orchestration Rules (Jobs, Tools & Factories)

`agent-core` はシステム全体を統括する司令塔であり、運用層です。`core-service`（ステートレスなドメインロジック）を呼び出して実行する際は、以下の構成とルールに従ってください。

## 1. Composition Root (`factories/`)
`core-service` の Service は、環境変数や設定を一切持ちません。そのため、`agent-core/factories/` 配下にサービスごとの **組み立て工場（Composition Root）** を作成します。
ここでは `agent-core/config/` 等から設定を読み込み、Config インスタンスと Repository インスタンスを生成して Service に注入（DI）し、完成した Service を返します。

### 🚫 ハードコードの完全禁止 (No Hardcoding Rule)
Factory（組み立て工場）内に、各種パスやディレクトリ名、APIキー等を**直書き（ハードコード）してはなりません**。
必ず `agent-core/config/conf.env` などの設定ファイルや環境変数から動的に値をパースし、設定変更時にコードの改修が不要な状態を保ってください。

## 2. 実行の入り口 (`jobs/` と `tools/`)
組み立て済みの Service は、以下の用途に応じて適切なディレクトリから呼び出してください。
- **`jobs/`**: 定期実行バッチ、深夜処理、`launchd` 等から直列で呼び出される自動化スクリプト。
- **`tools/`**: Agent が能動的に利用する検証ツールやユーティリティスクリプト。
