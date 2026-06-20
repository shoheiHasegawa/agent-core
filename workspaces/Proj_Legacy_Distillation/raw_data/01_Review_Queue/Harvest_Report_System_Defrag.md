# Harvest Report: System Defragmentation & Architecture Cleanup

## 📌 Context
- **Date**: 2026-06-08
- **Trigger**: `second-brain` および `life-automation` リポジトリの大規模なデフラグ・不整合解消セッションの完了

## 💡 Wisdom (得られた教訓・アーキテクチャの知見)
1. **インフラ層とApplication層のライフサイクルの一致**:
   - Application層のサービス（例: `zaim_sync`, `mail_capture`）を削除した際は、それに完全に依存しているInfrastructure層の「〇〇er」クラス（例: `ZaimAuthManager`, `MboxReader`等）も同時に削除しなければ、ゾンビコード（残骸）として残存してしまう。モジュールを削除する際は、「誰がそれを呼んでいるか」だけでなく「それが何を呼んでいるか」もトラッキングして刈り取る必要がある。
2. **テストコードの追従漏れ**:
   - プロダクションコードのディレクトリをリネーム（`cfo` -> `finance`等）した際、テスト側のディレクトリ名（`tests/infrastructure/cfo/` 等）の変更を忘れがちになる。今後はディレクトリ構造の変更時にテストディレクトリもセットで移行する。
3. **FacadeとOrchestratorの境界**:
   - `DailyPlanner` のように「何もドメインロジックを持たず、ただ内部のサービスを呼び出すだけのクラス」は不要なFacadeとなる。副作用（リポジトリからのLoad/Save）のオーケストレーションは、特別なFacadeクラスを設けるのではなく、Entry Point（CLI等）や専用のWorkflow関数で直接 `Application Service` と組み合わせて行うのが最もクリーンである。

## ⚠️ Tech Debt (技術的負債・積み残し)
1. **`infrastructure/finance/` の命名規則**:
   - 今回、極悪な「〇〇er（Manager, Reader等）」はインフラ層から一掃したが、`finance` 領域にはまだ `BudgetConfigLoader` や `RuleBasedClassifier` といった `er` 終わりのクラスが存在する。これらは極端な責務違反ではないものの、「ポート（インターフェース）の具象」としての命名（例: `JsonBudgetConfigAdapter`等）にいずれ統一する余地がある。
2. **テスト実行基盤（Linter/Pytest）のCI化**:
   - ローカルのテスト実行や `uv run ruff check` の検証をエージェントに依存している。これを pre-commit hook や CI パイプラインに組み込むことで、今回のような「インポートエラーの混入」を即座にブロックできる。

## 🚀 System Improvement (システム改善案)
- `verify_knowledge.py` による静的解析（Linter）は極めて有効であることが証明された。今後はナレッジベースだけでなく、`life-automation` のアーキテクチャ依存関係（例: DomainがInfrastructureに依存していないか）をチェックするアーキテクチャLinter（`pytest-arch` や独自スクリプト）の導入を推奨する。

## 🔎 追加の知見 (Second-Round Audit)
1. **Linterと目視の限界**:
   - `verify_knowledge.py` による静的チェックに加え、AIエージェントによるファイルツリー全体の「文脈的整合性（INDEXの記載漏れなど）」のダブルチェックが極めて有効であった。
2. **Review Queue の散乱**:
   - `Harvest_Report` などの中間生成物が `02_Review_Queue` 直下に溜まりやすい傾向がある。ルールで「トピックフォルダへ格納する」と規定していても、明示的なシステム制御（移動スクリプトや定期Defragタスク）がないと形骸化する。
