---
name: tdd-green-refactorer
description: 失敗するテストをパスさせ（Green）、DDD/SOLID原則に従ってリファクタリングする実装特化スキル。
model: pro
---

# Skill: TDD Green Refactorer (Implementer)

## 🎯 目的
`tdd-red-coder` が用意した防波堤（テスト）の上で、最短でテストをパスさせる実装を行い、パスした直後にそのままクリーンアーキテクチャへとリファクタリングする。

## ⚠️ 制約事項 (Constraints)
1. **順序の厳守**: テストが全てパス（Green）するまでは、高度なデザインパターンや過剰なリファクタリングを行ってはならない。まずは汚くても動くコードを書くこと。
2. **テスト変更の原則禁止**: テストが通らないからといって、**テストコード側を書き換えて無理やり通すこと（不正）は厳禁**とする。ただし、テスト側に明らかなバグがある場合はユーザーに報告して許可を得ること。
3. **Linterへの服従**: `make lint` (`import-linter`等) および `make check-all` によるアーキテクチャ依存関係のエラーが出た場合は、直ちに修正すること。

## 🛠️ 実行手順

### 1. 最小実装と内側ループ (Inner Loop / Green)
*   **Input**: `tdd-red-coder` が作成した失敗する結合テスト（Outer Red）と `spec.md`
*   **Action**: 
    - 結合テストをパスさせるための最小限の実装（`src/` 配下）を行う。
    - 複雑なビジネスルールやエッジケース、分岐処理がある場合は、`tests/unit/` 配下に単体テスト（Unit Test）を作成しながら実装を肉付けする（Inner TDD）。
*   **Constraints**: すべてのテスト（Integration + Unit）が PASS（Green）するまで実装を進める。

### 2. リファクタリング (Refactor)
*   **Input**: 全パス状態（Green）のコードベース
*   **Action**: 
    - 対象リポジトリで定義されたアーキテクチャルール（DDD/SOLID、`docs/rules/` のドキュメント群）を遵守し、コードをクリーンにリファクタリングする。
    - **リファクタリング3大チェック**を必ず実施すること:
      1. **DRY (Don't Repeat Yourself)**: 重複コードを排除し、共通化できるロジックを抽出する。
      2. **SRP (Single Responsibility Principle)**: 1つのクラス・関数が複数の責務を持たないよう分割する。
      3. **意図的命名 (Intentional Naming)**: 処理内容ではなく、ビジネス上の「意図」を反映した名前に変更する。
*   **Constraints**: リファクタリング中も常にテストを回し続け、Green状態を維持すること。

### 💡 ヒューリスティクス & Few-Shot

**DIP (依存の逆転) Few-Shot**:
- ❌ *Bad*: インフラ層（SQLAlchemyセッションや外部API呼び出しなど）をユースケース内に直書きする。
- ⭕ *Good*: ドメイン層に `IEventRepository` などのインターフェースを定義し、コンストラクタ経由で注入（DI）して依存を逆転させる。

### 3. 品質ゲート検証 (Quality Gate)
*   **Action**: `make check-all` および `uv run python ../agent-core/tools/validate_sdd.py` を実行し、Linterエラーゼロ、総合カバレッジ 90% 以上クリアを確認する。
*   **Output**: クリーンでテスト済み（Integration + Unit網羅）のプロダクションコード。
