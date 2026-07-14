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

### Phase 1: Tester Agent の起動
*   **入力 (Input)**: 要求されたユースケース (`spec.md` 等)
*   **アクション (Action)**: `invoke_subagent` を使用し、「Tester Agent」を起動してFailするテストコード（Red）だけを作成させる。
*   **制約事項 (Constraints)**: テスト関数のDocStringには必ず `[SCENARIO-XX]` の仕様IDを含めること。また、`core-service/src/` 配下の本番コードを編集させることは絶対に禁止する。
*   **出力 (Output)**: Testerからの完了報告

### Phase 2: Implementer Agent の起動
*   **入力 (Input)**: Testerが作成したテストコード
*   **アクション (Action)**: Testerからの完了報告を受けた後、`invoke_subagent` を使用し「Implementer Agent」を起動してテストをパスさせる（Green）最小限の実装を行わせる。
*   **制約事項 (Constraints)**: 実装は `core-service/src/` 直下のレイヤー責務に従うこと。コンファメーションバイアスを防ぐため、既存のテストコード（`tests/`配下）を書き換えることは絶対に禁止する。
*   **出力 (Output)**: Implementerからの完了報告

### Phase 3: Reviewer Gate (多段ゲート化による検証)
*   **入力 (Input)**: Implementerが実装したコード
*   **アクション (Action)**: **あなた自身がレビューするのではなく**、`invoke_subagent` で「Compliance Reviewer Agent」を起動し、`core-service/AGENT.md` から辿れる全ルール（DDDやDI等）に違反していないかを審査させる。
*   **制約事項 (Constraints)**:
    1. Reviewerから「検証パス（Pass）」の報告を得られない限り完了してはいけない。
    2. Rejectされた場合は再度Implementerを起動して修正させ、再検証ループを回すこと。
*   **出力 (Output)**: ReviewerからのApprove

### Phase 4: 全検証と完了
*   **アクション (Action)**: Reviewerのパスを得たら、最後に `core-service` ディレクトリ内で **`make check-all`** を実行する。
*   **出力 (Output)**: 自動テストがすべて通ることを確認した上での完了報告（Harvest Report）。
