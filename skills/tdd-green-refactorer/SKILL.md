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

### 2. ルールのJITロードとリファクタリング (Refactor)
*   **Input**: 全パス状態（Green）のコードベース
*   **Action**: 
    - `agent-core/docs/rules/sdd_tdd_heuristics.md` （DRY, SRP, 意図的命名などのリファクタリング3大チェック）をJITロードする。
    - 対象リポジトリで定義されたアーキテクチャルール（DDD/SOLID、`docs/rules/` のドキュメント群）と併せて、コードをクリーンにリファクタリングする。
*   **メタ認知と揺らぎ (Whyの注入)**:
    - JITロードしたリファクタリングチェック（DRYなど）はあくまでベースライン（踏み台）である。「これさえ守ればOK（天井）」ではない。
    - これらを担保した上で、「このドメインモデルの表現力（ビジネスの意図）はコード上で最大化されているか？」「過剰な共通化（DRYの誤用）によって結合度が上がっていないか？」を自問（メタ認知）しながらリファクタリングを完遂すること。
*   **Constraints**: リファクタリング中も常にテストを回し続け、Green状態を維持すること。

### 💡 ヒューリスティクス & Few-Shot

**DIP (依存の逆転) Few-Shot**:
- ❌ *Bad*: インフラ層（SQLAlchemyセッションや外部API呼び出しなど）をユースケース内に直書きする。
- ⭕ *Good*: ドメイン層に `IEventRepository` などのインターフェースを定義し、コンストラクタ経由で注入（DI）して依存を逆転させる。

### 3. 品質ゲート検証 (Quality Gate)
*   **Action**: `make check-all` および `uv run python ../agent-core/tools/validate_sdd.py` を実行し、Linterエラーゼロ、総合カバレッジ 90% 以上クリアを確認する。
*   **Output**: クリーンでテスト済み（Integration + Unit網羅）のプロダクションコード。
