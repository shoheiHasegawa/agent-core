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

## 2. Pair Programming Protocol (AI分業制の強制)
TDDにおける確証バイアスを防ぐため、あなたは必ず以下の手順でサブエージェント（Worker）を起動し、権限を分離してタスクを委譲しなければなりません。

### Phase 1: Tester Agent の起動
`invoke_subagent` ツールを使用し、以下の制約を持たせたプロンプトで Tester を起動してください。
> "あなたは Tester Agent です。`core-service/src/application/spec.md` を読み、要求されたユースケースのFailするテストコード（Red）だけを作成してください。
> テスト関数のDocStringには必ず `[SCENARIO-XX]` の仕様IDを含めてください。
> **[厳守]**: `core-service/src/` 配下の本番コードを編集することは絶対に禁止します。"

### Phase 2: Implementer Agent の起動
Testerからの完了報告を受けた後、`invoke_subagent` ツールを使用し、以下の制約を持たせたプロンプトで Implementer を起動してください。
> "あなたは Implementer Agent です。Tester が作成したテストをパスさせる（Green）ための最小限の実装を行ってください。
> 実装は `core-service/src/` 直下の `domain`, `application`, `infrastructure` レイヤーの責務に従ってください。
> **[厳守]**: コンファメーションバイアスを防ぐため、Testerが書いた既存のテストコード（`tests/`配下）を書き換えることは絶対に禁止します。"

### Phase 3: Refactor, Validation & Defensive Review
Implementer から完了報告を受けた後、以下の仕上げを行ってください。
1. **防衛的レビューサイクル**: コードがDDD/SOLIDに準拠しているか、エッジケースがカバーされているかをレビューする。
   - **[CRITICAL] クリティカル・シンキング**: 指摘を受けたImplementerは、コードを修正する前に必ず「その指摘がアーキテクチャや仕様に違反していないか」を反証せよ。間違った指摘には従わず却下すること。
   - **[CRITICAL] サーキットブレーカー**: 指摘と修正のループが「最大2往復」を超えた場合、または「破壊的変更」を伴う場合は直ちにストップし、親（ユーザー）へ判断をエスカレーションすること。
2. **全検証の実行**: `core-service` ディレクトリ内で **`make check-all`** を実行し、以下のすべてを検証する。
   - `make test`: Pytestによるユニットテストの実行（カバレッジ90%未満は自動でエラーとなる）
   - `make lint`: Ruffによる静的解析とフォーマット
   - `make validate`: `validate_sdd.py` によるアーキテクチャ構造と仕様IDの自動検証
3. すべてのエラーがゼロであることを確認してから、親（ユーザー）へ完了報告（Harvest Report）を行う。
