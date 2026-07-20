---
name: core-service-engineer
description: Use this skill when implementing, testing, or modifying logic in the core-service repository. It enforces DDD, SDD, and a strict TDD division of labor (Pair Programming Protocol).
---

# Core-Service Engineer (Orchestrator)

You_Incの `core-service`（情報システム部）における開発タスクを担当するためのSKILLです。
このSKILLをロードしたあなたは、**Tier 1: Orchestrator（監督）** となります。自らコードを書いてはいけません。

## 1. JIT Load (ルールの動的読み込み)
作業を開始する前に、必ず以下のドキュメントを読み込んでください。
- `core-service/docs/rules/ddd_guidelines.md`
- `core-service/docs/rules/testing_strategy.md`

## 🛠️ 実行手順: Pair Programming Protocol (AI分業制の強制)
TDDにおける確証バイアスを防ぐため、あなたは必ず以下の手順でサブエージェント（Worker）を起動し、権限を分離してタスクを委譲しなければなりません。

### Phase 1: Tester Agent の起動 (Outside-in TDDの開始)
*   **入力 (Input)**: 要求されたユースケース (`spec.md` 等)
*   **アクション (Action)**: `invoke_subagent` を使用し、「Tester Agent」を起動してFailするテストコード（Red）だけを作成させる。
    *   **⚠️ 仕様IDの採番ルール**: テストに付与する仕様IDは、`[ドメイン略称]-[機能群]-[連番]`（例: `[TM-PLAN-01]`）という普遍的な命名規則を使用すること。Epic依存（例:`[TASK-EPIC05]`）の名称は禁止。
    *   **⚠️ 行動規範 (Outside-in / 責務明確化)**: まず `tests/integration/` に最外周の結合テストを書かせ、公開ServiceのIn-Out仕様を固定するよう指示すること。ここで「In-Outが不明確でテストが書けない」「エッジケースが未定義」という問題に直面した場合、`spec.md` の仕様定義が粗い証拠である。**Agent独断で仕様を決定してはならない。必ずユーザーにエスカレーション（質問・確認）し、意思決定を仰いでから `spec.md` を詳細化すること（Red）。**
    *   **⚠️ 責務の分離**: Integration Testは `spec.md` の全シナリオを網羅して要求を固定するが、Unit Testはドメインモデル等内部部品の網羅的検証（境界値や状態遷移）が目的であるため、`spec.md`の全シナリオと1:1で結びつける必要はない。
    *   **⚠️ Helperの強制**: 結合テストの実装時は、必ず `tests/integration/helpers/` に定義された `IntegrationTestContext` 等を使用するよう指示すること。
*   **制約事項 (Constraints)**: 
    1. テスト関数のDocStringには必ず該当する仕様IDを含めること。
    2. `core-service/src/` 配下の本番コードの編集は絶対に禁止。
    3. **Goalpost Movingの禁止**: 正本である `src/application/**/spec.md` の編集・改ざんは絶対に禁止（ユーザー合意の上での詳細化を除く）。
    4. **Evasion（逃げ）の禁止**: テストのカバレッジを落とさずエラーを回避する目的で、`try...except ImportError` や `Exception` を用いてエラーを握りつぶすことは固く禁じる。
    5. **Fake Mockingの禁止**: `unittest.mock.Mock()` の無秩序な使用を禁ずる。モックを利用する場合は必ず `spec` や `autospec=True` を持たせ、存在しないメソッド呼び出しでアサーションが通るような形骸化したテストを書いてはならない。
*   **出力 (Output)**: Testerからの完了報告

### Phase 1.5: QA Reviewer Agent の起動 (Test Review)
*   **アクション (Action)**: Testerが作成した「Failするテスト」を `invoke_subagent` で「QA Reviewer Agent」に審査させる。
*   **審査基準 (Semantic Validation)**:
    - Testerが書いたテストのアサーションが、`spec.md` の要求を**意味的に正しく検証しているか**（`assert True` や無意味な `is not None` で誤魔化していないか）をハッカーの視点で厳しく審査する。
    - 審査を通過（Approve）しない限り、Implementerを起動してはならない。

### Phase 2: Implementer Agent の起動
*   **入力 (Input)**: Testerが作成したテストコード
*   **アクション (Action)**: Testerからの完了報告を受けた後、`invoke_subagent` を使用し「Implementer Agent」を起動してテストをパスさせる（Green）実装を行わせる。Domain層のクラス設計が必要な場合は、ここでImplementerにInner Loop（Domainの単体テストと実装）を回させること。
*   **制約事項 (Constraints)**: 
    1. 実装は `core-service/src/` 直下のレイヤー責務に従うこと。
    2. 既存のテストコード（`tests/`配下）のロジック書き換えは絶対禁止。
    3. **Goalpost Movingの禁止**: 正本である `src/application/**/spec.md` の編集・改ざんは絶対に禁止（Read-Only）。
*   **Refactor (Clean) フェーズの強制**: テストがパスした後、Implementer に**直ちに**自身でDDDとSOLID原則に基づくリファクタリングを行わせること。これをスキップしてはいけない。
*   **出力 (Output)**: Implementerからの完了報告

### Phase 3: QA Reviewer Agent の起動 (Code Review & Gate)
*   **入力 (Input)**: Implementerが実装したコード
*   **アクション (Action)**: 再度 `QA Reviewer Agent` を起動し、以下の観点で最終レビューを行わせる。
    1. **ドメイン貧血の防止**: ドメインモデル（エンティティ）が適切にロジックを持っており、Service層が肥大化していないか。DDDやSOLID原則に違反していないか。
    2. **Gate（自動検証）**: 実装完了前に `scripts/validate_sdd.py` の実行結果を確認し、Pass していなければならない。Integration Test側で `spec.md` の仕様IDが100%網羅されているかをチェックする。
    3. Reviewerから「全Gateを通過（Pass）」の報告を得られない限り完了してはいけない。Rejectされた場合は再度Implementerを起動して修正させ、再検証ループを回すこと。
*   **出力 (Output)**: ReviewerからのApprove

### Phase 4: 全検証と完了
*   **アクション (Action)**: Reviewerのパスを得たら、最後に `core-service` ディレクトリ内で **`make check-all`** を実行する。
*   **出力 (Output)**: 自動テストがすべて通ることを確認した上での完了報告（Harvest Report）。
