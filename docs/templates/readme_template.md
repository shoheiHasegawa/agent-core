# [Feature Name]

## 1. Context & Objective (背景と目的)
- **Why (なぜ必要なのか)**: You_Incとしてこの機能が存在するビジネス的な理由、解決したいユーザーの課題。
- **What (何を実現するのか)**: この機能がシステムに提供する価値の概要。

## 2. Architecture & Data Flow (アーキテクチャ)
- 外部システム、他ドメイン、あるいは内部モジュールとの連携を図解または箇条書きで説明する。
- （必要に応じてMermaidダイアグラムを使用する）

## 3. Routing & Navigation (関連ファイルへのポインタ)
当機能に関する主要なファイル群へのリンク（ポインタ）。開発やテストを行う際は以下を参照すること。

- **仕様書 (Contract & Scenarios)**: [spec.md](./spec.md)
- **エントリーポイント (Facade/UseCase)**: [実装ファイル名.py](./*.py)
- **結合テスト (Integration Tests)**: `../../../../tests/integration/[domain_name]/`
- **単体テスト (Unit Tests)**:
  - Application: `../../../../tests/unit/application/[feature_name]/`
  - Domain: `../../../../tests/unit/domain/[entity_name]/` (※関連するエンティティや値オブジェクトのテスト群)
  - Infrastructure: `../../../../tests/unit/infrastructure/[adapter_name]/` (※関連するインフラ層のテスト群)
