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

### Phase 1: Tester Agent の起動 (Double-Loop TDDの開始)
*   **入力 (Input)**: 要求されたユースケース (`spec.md` 等)
*   **アクション (Action)**: `invoke_subagent` を使用し、「Tester Agent」を起動してFailするテストコード（Red）だけを作成させる。
    *   **⚠️ 行動規範 (Outer Loop -> Inner Loop)**: Tester Agentには、まず `tests/integration/` に最外周の結合テストを書かせ、次に `tests/unit/application/` にApplication層の単体テストを書かせるよう指示すること。（Domain層等の詳細な単体テストは、Phase 2でImplementerに書かせてよい）。
    *   **⚠️ Helperの強制**: 結合テストの実装時は、必ず `tests/integration/helpers/` に定義された `IntegrationTestContext` 等を使用するよう指示すること。
*   **制約事項 (Constraints)**: 
    1. テスト関数のDocStringには必ず `[SCENARIO-XX]` の仕様IDを含めること。
    2. `core-service/src/` 配下の本番コードの編集は絶対に禁止。
    3. **Goalpost Movingの禁止**: 正本である `src/application/**/spec.md` の編集・改ざんは絶対に禁止（Read-Only）。
*   **出力 (Output)**: Testerからの完了報告

### Phase 2: Implementer Agent の起動
*   **入力 (Input)**: Testerが作成したテストコード
*   **アクション (Action)**: Testerからの完了報告を受けた後、`invoke_subagent` を使用し「Implementer Agent」を起動してテストをパスさせる（Green）実装を行わせる。Domain層のクラス設計が必要な場合は、ここでImplementerにInner Loop（Domainの単体テストと実装）を回させること。
*   **制約事項 (Constraints)**: 
    1. 実装は `core-service/src/` 直下のレイヤー責務に従うこと。
    2. 既存のテストコード（`tests/`配下）のロジック書き換えは絶対禁止。
    3. **Goalpost Movingの禁止**: 正本である `src/application/**/spec.md` の編集・改ざんは絶対に禁止（Read-Only）。
*   **Refactor (Clean) フェーズの強制**: テストがパスした後、Implementer に**直ちに**自身でDDDとSOLID原則に基づくリファクタリングを行わせること。これをスキップしてはいけない。
*   **出力 (Output)**: Implementerからの完了報告

### Phase 3: Reviewer Gate (多段ゲート化による検証)
*   **入力 (Input)**: Implementerが実装したコード
*   **アクション (Action)**: **あなた自身がレビューするのではなく**、`invoke_subagent` で「Compliance Reviewer Agent」等を起動し、`core-service/AGENT.md` から辿れる全ルール（DDDやDI等）に違反していないかを審査させる。
*   **制約事項 (Constraints & Gate)**:
    1. **Gate（要求IDの網羅）**: Reviewer には、`tests/unit/` と `tests/integration/` の両方に `[SCENARIO-XX]` が付与されているかを厳格にチェックさせること。
    2. **Gate（自動検証）**: 実装完了前に `scripts/validate_sdd.py` の実行結果を確認し、Pass していなければならない。
    3. Reviewerから「全Gateを通過（Pass）」の報告を得られない限り完了してはいけない。Rejectされた場合は再度Implementerを起動して修正させ、再検証ループを回すこと。
*   **出力 (Output)**: ReviewerからのApprove

### Phase 4: 全検証と完了
*   **アクション (Action)**: Reviewerのパスを得たら、最後に `core-service` ディレクトリ内で **`make check-all`** を実行する。
*   **出力 (Output)**: 自動テストがすべて通ることを確認した上での完了報告（Harvest Report）。
