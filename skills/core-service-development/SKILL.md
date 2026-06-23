---
name: core-service-development
description: Use this skill when developing, refactoring, or testing features in the core-service repository. It contains strict rules for the Service-Config pattern and Dependency Injection.
---

# 🛡️ Core-Service Development Skill

## 1. 責務の分離原則
`core-service` は純粋なドメインロジックの集合（ステートレス工場）です。
- **外部環境へのアクセス禁止**: `core-service` 内に `.env` を読んだり、APIキーをハードコードしてはいけません。
- **実行は `agent-core` へ**: 自身を実行するスクリプト（バッチやツール）は `core-service` に置かず、`agent-core` の `jobs/` または `tools/` に配置してください。

## 2. Service-Config パターン（依存性注入）
機密情報やパス情報は必ず「Service-Config」パターンを用いて外部から注入（DI）してください。
- `core-service` 側には、機能が必要とする設定の型（`dataclass`）のみを定義します。
- `agent-core` 側の `factories/` ディレクトリ内で、実際の設定ファイルを読み込んで Config インスタンスを組み立て、Service に注入します。
  - ⚠️ **[CRITICAL] Factory内でのハードコード禁止**: `factories/` のコード内にパスやURL等のリテラルを直書きしてはいけません。必ず `config/conf.env` 等から動的に読み込む実装にしてください。

👉 詳細は `core-service/docs/rules/dependency_injection.md` および `agent-core/factories/zettelkasten.py` の実装手本を参照してください。
