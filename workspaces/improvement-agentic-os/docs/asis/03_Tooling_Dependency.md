# 03_Tooling_Dependency (AS-IS)

## 1. 概要
現状のアーキテクチャにおいて、Agentが使用するツール群（スクリプトやテスト実行環境）は、システムとLLMの間に立つ「Gatekeeper（防波堤）」として十分に機能していません。本ドキュメントでは、ツール群がどのようにエラー出力を隠蔽し、LLMの自己修復（Self-healing）プロセスを妨げているかを図解とともに詳述します。

## 2. Gatekeeper機能の欠如による自己修復の阻害
既存の監査レポート（Tooling Auditor等）の調査結果から、以下の要因によりエージェントのエラー回復が困難になっていることが判明しています。

1. **エラー出力の隠蔽（Truncation）**
   テスト実行ツール（`verify_loop_state.py`等）は、エラー発生時に長大なログ出力を単に末尾から切り捨てる（スライスする）処理を行っています。この結果、スタックトレースの根本原因やアサーションエラーの詳細なdiffがLLMに伝わらず、修正アクションを起こすためのコンテキストが失われます。
2. **入力検証の脆さ（Weak Validation）と不親切なエラー**
   `update_task.py` 等において、Enum（列挙型）のパースや境界値検証が不十分です。不正な値が渡された際、単にPythonの `KeyError` などを吐き出してしまい、「利用可能な選択肢は何か」といったアクション可能なエラーメッセージ（Actionable Error）をLLMにフィードバックできていません。
3. **スキーマバリデーションの欠如**
   ツール側で受け取るJSONペイロードに対する構造的な事前検証が弱く、内部のドメインロジックで予期せぬエラーやハング（STDINのデッドロック等）を誘発しています。

## 3. 現状のツール依存関係と課題の図解

以下の図は、LLMエージェントからツールへのリクエストフローと、現状のツールがいかにしてフィードバックループ（自己修復）を阻害しているかを示しています。

```mermaid
graph TD
    %% Entities
    Agent[LLM Agent]
    System[Domain Services / Backend]
    TestRunner[Test Runner / Pytest]
    
    %% Tooling Layer
    subgraph Tooling_Layer [Tooling Layer (Poor Gatekeepers)]
        direction TB
        Tool_Test[verify_loop_state.py<br/>(テスト実行・検証)]
        Tool_Input[update_task.py / process_inbox_item.py<br/>(状態更新・入力処理)]
        Tool_Data[register_zettelkasten_note.py<br/>(データ登録)]
    end
    
    %% Flow and Failures
    Agent -->|1. テスト実行要求| Tool_Test
    Tool_Test -->|実行| TestRunner
    TestRunner -->|長大なエラーログ| Tool_Test
    Tool_Test -.->|2. 末尾切り捨て(Truncation)<br/>原因箇所が消失| Agent
    
    Agent -->|3. ハルシネーションによる<br/>不正なEnum/パラメータ| Tool_Input
    Tool_Input -.->|4. KeyError等<br/>利用可能な選択肢が提示されない| Agent
    Tool_Input -->|脆弱なバリデーションのまま通過| System
    
    Agent -->|5. 不正なJSON / STDIN入力| Tool_Data
    Tool_Data -.->|6. ハングアップ / 場当たり的なエラー| Agent
    Tool_Data -->|暗黙の検証| System
    
    %% Styling
    classDef fail stroke:#f66,stroke-width:2px,stroke-dasharray: 5 5;
    class Tool_Test,Tool_Input,Tool_Data fail;
```

## 4. ツールごとの具体的な脆弱性

- **`verify_loop_state.py`**: 
  テスト失敗時、`combined[-1000:]` のように末尾の固定文字数のみをスライスして返却しています。これにより、最も重要なエラー原因（スタックトレースのトップやテストの差分）が隠蔽され、LLMが「なぜ落ちたのか」を読み取れず、修正不能な無限ループに陥る原因となっています。
- **`update_task.py` / `process_inbox_item.py`**: 
  Enumのデシリアライズに脆さがあり、無効な文字列が渡されると組み込みの `KeyError` が発生します。また、ツール間で定義されている選択肢（`Normal` の有無など）に不整合があり、LLMが別のツールの経験から推測して入力した値が弾かれる問題も生じています。
- **`register_zettelkasten_note.py`**: 
  標準入力（STDIN）パイプラインからの読み取りにおいてデッドロック（ハング）のリスクがあります。さらに、JSONスキーマに対する明確なGatekeeper機能が存在せず、エラー時に「正しいスキーマ定義」をLLMに提示できません。
- **`validate_sdd.py` (Linter)**: 
  AST（抽象構文木）解析による静的なモック使用検知に依存しているため、動的インポートなどによる制限の回避（Evasion）を完全に防ぐことができていません。
