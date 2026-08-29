# Agentic OS 責務の再配置とグラフ化 (Blackboard / PubSub モデルの導入)

ユーザーから提起された「1 Agentあたりの責務が大きすぎる」「Agent間で呼び出し合うことでオーケストレーションが複雑化している」という仮説を可視化・整理します。

## 現状の複雑なグラフ（Fat Orchestration / Daisy Chain）

現状のYou_Incでは、Agentが別のAgentを同期的に呼び出し（invoke_subagent）、結果を待つという直列的な依存関係が構築されています。

```mermaid
graph TD
    User([User]) -->|依頼| Orchestrator[Orchestrator Agent]
    Orchestrator -->|調査・実装依頼| Worker[Worker Agent]
    
    subgraph "Fat Worker (過剰な責務)"
        Worker -->|コード記述| Code[(Source Code)]
        Worker -->|レビュー依頼 (待機)| Reviewer[Reviewer Agent]
        Reviewer -.->|フィードバック| Worker
        Worker -->|コンプライアンス依頼 (待機)| Compliance[Compliance Agent]
        Compliance -.->|パス| Worker
    end
    
    Worker -.->|完了報告| Orchestrator
```

**現状の問題点（Fat Worker / Fat Orchestrator）**:
- **同期待機**: Worker Agentはレビューやコンプライアンス検証が終わるまでコンテキストを保持して待機しなければならない。
- **責務過多**: 実装者が「自身のレビューをオーケストレーションする」というメタ作業を負っている。
- **コンテキストの肥大化**: 複数のやり取りが1つのAgentの履歴（Transcript）に蓄積し、オーバーロード（忘却）を引き起こす。

---

## 提案される薄いグラフ（Thin Orchestration / Blackboard Queue）

「Agent間のやり取りをする場所（掲示板 / Task Registry）」を新設し、各Agentは**「自分の作業をして、結果を掲示板に書いて死ぬ（終了する）」**というPub/Sub的な非同期メッセージパッシングモデルへ移行します。

```mermaid
graph TD
    User([User]) -->|依頼| Orchestrator[Thin Orchestrator Agent]
    
    subgraph "Blackboard / Message Queue (掲示板)"
        Registry[(Task Registry / Event Queue)]
    end
    
    Orchestrator -->|タスク生成| Registry
    Orchestrator -->|Workerを単発起動| Worker[Worker Agent]
    
    Worker -->|1. コード記述| Code[(Source Code)]
    Worker -->|2. 完了＆レビュー依頼を書き込む| Registry
    Worker -.->|終了 (コンテキスト破棄)| Grave((End))
    
    Registry -.->|イベント検知: Review Requested| Orchestrator
    Orchestrator -->|Reviewerを単発起動| Reviewer[Reviewer Agent]
    
    Reviewer -->|1. レビュー実行| Code
    Reviewer -->|2. 結果を書き込む| Registry
    Reviewer -.->|終了| Grave
    
    Registry -.->|イベント検知: Review Passed| Orchestrator
    Orchestrator -->|ユーザーへ報告| User
```

**新モデルの利点（引き算と責務移譲）**:
- **Stateless Agent**: 各Agentは単一の役割（SOLID原則における単一責任の原則）のみを持ち、終われば消滅するためコンテキストが肥大化しない。
- **Thin Orchestrator**: 司令塔は「掲示板（Queue）を見て、次に必要なAgentを叩き起こすだけ」となり、複雑な思考や待機が不要になる（スクリプト化も視野に入るレベル）。
- **Hard Constraintの容易さ**: Agent同士が直接会話するのではなく、必ず掲示板（DBやファイル）を経由するため、システム側で「指定されたフォーマットで書き込まれているか？」「必須テストは通っているか？」をフック（Gatekeeper）で検閲しやすくなる。
