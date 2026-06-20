# 06. Knowledge Build Pipeline & Source-Compiled Architecture

> [!WARNING]
> **Status: Deprecated** (この決定事項は最新の `to-be/` アーキテクチャに統合・置換されました)

## 概要
本ドキュメントは、「You, Inc.」アーキテクチャにおける知識の管理とAIへの統合フローを定義します。
最大の特徴は、**ローカル環境（Obsidian + Git）を「知識のソースコード（SSOT）」とし、NotebookLM（Google Drive）を「コンパイル済みの実行用バイナリ」として扱う**設計思想です。

## 1. 全体アーキテクチャ図 (Source vs Compiled)

```mermaid
graph TD
    subgraph Local_Git["Local / Git (Source Code) - SSOT"]
        direction TB
        R["📁 30_Resources\n(階層あり: 日誌, 資料, 生データ)"]
        Z["📁 40_Permanent_Notes\n(完全フラット: C-Q-A原則群)"]
        R -- 抽出と意味付け --> Z
    end

    subgraph CI_CD["Build Pipeline (Python Script)"]
        direction LR
        Extract["タグ抽出\n(例: #context/trading)"]
        Deploy["Driveへデプロイ"]
        Extract --> Deploy
    end

    subgraph Cloud_Execution["Cloud / NotebookLM (Compiled Binary)"]
        direction TB
        N_Trader["NotebookLM (Trader)"]
        N_Arch["NotebookLM (Architect)"]
    end

    subgraph AntiGravity_UI["AntiGravity (agent-core)"]
        direction TB
        A_Trader["🤖 Trader Agent\n(Persona)"]
        A_Arch["🤖 Architect Agent\n(Persona)"]
    end

    Z -- タグベースでフィルタ --> Extract
    Deploy --> N_Trader
    Deploy --> N_Arch

    A_Trader -- 読み込み (Harness) --> N_Trader
    A_Arch -- 読み込み (Harness) --> N_Arch
```

## 2. ディレクトリ構造の責務分離

| ディレクトリ | 性質・責務 | 構造 | 命名規則・メタデータ |
| :--- | :--- | :--- | :--- |
| **`30_Resources`** | Permanent Notesの「材料」。生データ、他者の記事、トレード日誌、スクショ等。 | **浅い階層構造**（人間が目視検索しやすいため） | 名詞ベース、時系列ベース（例: `20260613_EURUSD.md`） |
| **`40_Permanent_Notes`** | 純粋な「主張・原理原則」。抽出され、結晶化されたYou, Inc.の哲学。 | **完全フラット**（Agentの抽出を最適化するため） | 命題ベース（例: `損切りは未来への再投資である.md`）。文脈はタグで管理 |

### ※ `30_Resources` の名称について
もし「Resources」という言葉が広義すぎて曖昧さを生む場合、`30_Logs_and_References` や `30_Raw_Materials` といった名前に変更することも検討の余地がありますが、PARAメソッド（Projects, Areas, Resources, Archives）への準拠という観点から、まずは `30_Resources` の名称を維持しつつ「Permanent Notesの素材庫である」という責務を明文化して運用します。

## 3. 知識のビルドとハーネスのシーケンス

トレード日誌の記録から、AIエージェントによるトレード戦略アドバイスまでの情報の流れ（フロー）を示します。

```mermaid
sequenceDiagram
    actor User as Human (You, Inc.)
    participant Res as 📁 30_Resources
    participant Zk as 📁 40_Permanent_Notes
    participant Build as ⚙️ Build Script
    participant NLM as 🧠 NotebookLM (Drive)
    participant Agent as 🤖 Trader Agent

    User->>Res: 1. トレード日誌（画像・反省点）を記録
    User->>Zk: 2. 日誌から教訓を抽出・C-Q-A化 (タグ: #context/trading)
    Note over Zk: ファイル: エントリーの前提が崩れたら即撤退する.md
    Zk-->>Res: 3. 証拠として日誌へのリンクを埋め込み
    loop 定期実行 / トリガー
        Build->>Zk: 4. #context/trading を検索
        Build->>NLM: 5. 該当ファイルを同期（デプロイ）
    end
    User->>Agent: 6. 「今日の戦略を相談したい」
    Agent->>NLM: 7. RAGクエリ（独自の哲学のみを参照）
    NLM-->>Agent: 8. あなたの過去の失敗に基づく独自のコンテキスト
    Agent-->>User: 9. あなたのルールに忠実な戦略の提案
```
