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

## 3. アーキテクチャ命名規則（Naming Conventions）
ドメイン層とインフラ層の関心事を分離し、AIのハルシネーション（エイリアス等）を防ぐため、以下の命名規則を厳守してください。
- **Interface Naming Rule (Domain層)**: インターフェース名はドメイン概念をそのまま表す名称（例: `TaskRepository`, `IssueParser`）を使用してください。C#やJavaに見られるようなインターフェース特有の接頭辞（例: `ITaskRepository`）を付与してはなりません。
- **Implementation Naming Rule (Infrastructure層)**: 実装クラスには必ず技術的詳細を示す接頭辞を冠してください（例: `SqlTaskRepository`, `LocalFileMobileVaultRepository`）。インターフェースと同名にすることは（importエイリアスが必要になるため）厳禁です。

## 4. リソース管理のベストプラクティス（DBセッション等）
エントリポイント（バッチスクリプトやCLIツール）等においてデータベースのセッションを生成・管理する際は、必ず `with SessionLocal() as session:` のようにコンテキストマネージャー（with 句）を使用し、異常時にも確実にリソースが解放される堅牢な設計（PEP 343準拠）を標準方針としてください。`try-finally` によるレガシーな手動クローズ管理は禁止とします。
