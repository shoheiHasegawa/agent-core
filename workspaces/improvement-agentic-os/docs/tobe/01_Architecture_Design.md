# 01. TO-BE アーキテクチャ設計 (Real TO-BE)

## 1. 概要
目標とするアーキテクチャは、従来の「Daisy Chain (数珠つなぎ)」モデルから「Thin Orchestrator + Blackboard (PubSub)」モデルへと移行します。
`core-service` の実コードベースに基づき、この設計は既存の `task_management` インフラを尊重しつつ、Agent OSのタスク専用の隔離された新ドメインを導入します。

## 2. アーキテクチャモデル

### 2.1 Daisy Chain から Interactive Trigger モデルへ
完全に自律的なバックグラウンドのWatchdog（複雑でありゾンビAgentを生むリスクがある）を構築する代わりに、Thin Orchestrator は **対話フロントAgent (Session Manager)** 自身が担います。
- **Trigger (起動)**: ユーザーがフロントAgentに指示を出します。フロントAgentはコマンドを解釈し、Task Registry (DB) にタスクを登録して、Workerとなるサブエージェントを起動します。
- **Worker (実行者)**: WorkerはDBからタスクをチェックアウト（ロック）して実行し、完了状態にします。もしWorkerが失敗した場合、フロントAgentは対話の中でその失敗に気づき、リカバリを提案することができます。

### 2.2 システム構成図

```mermaid
graph TD
    subgraph ユーザーとの対話
        U[User] -->|チャット/コマンド| F[フロント Agent / Session Manager]
    end

    subgraph core-service DB (you_inc_ops.db などの永続化層)
        DB[(agent_tasks テーブル)]
    end

    subgraph Worker プール
        W1[Worker Agent A]
        W2[Worker Agent B]
    end

    F -->|1. タスク作成 (PENDING)| DB
    F -->|2. invoke_subagent で起動| W1
    F -->|2. invoke_subagent で起動| W2

    W1 -->|3. チェックアウト (CAS) & 実行| DB
    W2 -->|3. チェックアウト (CAS) & 実行| DB
```

## 3. 主要コンポーネントと相互作用

### 3.1 ドメインの隔離 (`agent_system`)
- 既存の `task_management` ドメインは人間（ユーザー）向けに維持されます。
- 新しい `agent_system` ドメインは、Agent OSの内部プロセス専用として作られます。
- 同じ物理DBファイルを使用しても、テーブル（`agent_tasks`）を分けることでスキーマの衝突を防ぎます。

### 3.2 SQLAlchemy CAS (Compare and Swap)
- 複数のWorkerが同じ PENDING タスクを同時にチェックアウトしようとする可能性があります。
- Spike検証 (`scratch/spike_cas.py`) により、`session.query().filter(status="PENDING").update(...)` というアトミックな操作で、必ず1体のWorkerだけがタスクを確保できることが証明されました。
- これにより、以前のファイルベース（`progress.md`）で発生していた状態管理のRace Condition（競合）やAmnesia（記憶喪失）が完全に排除されます。
