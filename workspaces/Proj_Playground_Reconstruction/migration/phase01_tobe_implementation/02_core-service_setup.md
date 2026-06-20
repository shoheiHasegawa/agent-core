# Phase01: core-service 初期実装タスク

## 1. 目標
情報システム部として、Agentの状態(State)を一切持たず、副作用(外部APIやDB)をカプセル化したステートレスで堅牢なドメインロジック/APIのスケルトンを構築する。

## 2. ディレクトリ構造の作成
以下のDDD（レイヤードアーキテクチャ）ディレクトリを初期作成する。
- `docs/rules/` (JITロードされる詳細ルール群)
- `src/domain/` (ドメインモデル)
- `src/application/` (ユースケースのオーケストレーション)
- `src/infrastructure/` (外部IFのAdapter)
- `tests/unit/`
- `tests/integration/`

## 3. 必須ファイルの作成
### 3.1. ルートファイル
- `README.md` (薄いルーター、ルールの在処のポインタ)
- `INDEX.md` (詳細ディレクトリマップ)

### 3.2. ドキュメントファイル (`docs/` 配下)
- `docs/architecture.md`
- `docs/review.md`
- `docs/rules/ddd_guidelines.md`
- `docs/rules/api_gateway.md`

## 4. 基盤コード・仕組みの実装要件
- **SDD (Specification Driven Development) 導入**: `src/application/` 内にユースケース単位の `spec.md` を配置し、仕様書内にシナリオID (`[SCENARIO-XX]`) を付与する仕組みの導入。
- **コンテナ化不要のステートレス設計**: `core-service` 自体のコンテナ（Docker）化は行わず、純粋なPythonライブラリ群として実装する。
- **静的解析と儀式の強制**: `ruff`（フォーマッタ・Linter）を導入し、`pre-commit` フックを用いてコミット前に静的解析（DDDレイヤー違反チェック等）を強制的に実行させる。
- **仕様とテストのトレーサビリティ**: `tests/` コードからシナリオIDを参照するルールの設定。
- **DIによるシークレット管理**: APIキー等を一切保持せず、実行時に `agent-core` 側から sops を経由して注入される仕組みを前提とする。
- **品質ゲート(CI)の準備**: GitHub Actions等によるテストカバレッジチェック、自動CIゲート（仕様化テスト）のスケルトン構築。
