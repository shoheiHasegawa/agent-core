# ADR 0009: Define 90_Meta Architecture and Progressive Migration Strategy

## Date
2026-06-13

## Context
「You, Inc.」の Agent-Centric アーキテクチャへの移行に伴い、旧システムで `99_System` として運用されていたディレクトリの扱いが課題となった。
`99_System` には、実行ロジックである自動化スクリプト（Automations）と、静的メタデータであるテンプレートや添付ファイル（Templates, Attachments）が混在しており、これは「データ層（Vault）」と「実行層（Agent OS）」の分離というアーキテクチャの根本原則に違反していた。

## Decision
1. **`90_Meta` としての再定義**: 
   最新の `to-be/20_second-brain_architecture.md` に記載の通り、旧 `99_System` は `90_Meta` として再定義する。
   `90_Meta` は、**「非セマンティックデータ（メタデータ）の隔離領域 (Quarantine Zone)」** という厳格な責務を持つ。Vault内におけるRAG（Retrieval-Augmented Generation）探索の対象外境界（**RAG Exclusion Boundary**）として機能し、ここに意味を持つナレッジを置くことは禁止される。
2. **段階的移行（Progressive Migration）に基づく除外**:
   ADR 0004 に則り、新規リポジトリ `second-brain` を構築する際、旧 `99_System/Automations` 等の「実行ロジック（Compute層）」は新Vaultへの移行対象から除外する。実行ロジックは必要に応じて `agent-core` (Agent OS) や `core-service` (仕事道具) 側で再実装する。
3. **Orphaned Attachments の自動パージ**:
   トレード日誌などで多用される画像（Attachments）は `90_Meta/Attachments/` に一元管理する。"Distill or Delete" フロー（ADR 0008）の実行時、AgentはMarkdownから参照されなくなった孤立画像（Orphaned Images）を検知し、自動的にガベージコレクション（削除）する。

## Flow / Diagram: RAG Exclusion Boundary

```mermaid
graph TD
    subgraph Agent OS [agent-core / Agent OS]
        RAG[RAG Query / Semantic Search]
    end

    subgraph Knowledge Vault [second-brain]
        RAG -->|Read/Parse| D00[00_Inbox]
        RAG -->|Read/Parse| D20[10_Areas]
        RAG -->|Read/Parse| D30[30_Resources]
        RAG -->|Read/Parse| D50[40_Permanent_Notes]
        
        RAG -.-x|Access Blocked<br/>(RAG Exclusion Boundary)| D90[90_Meta]
        
        subgraph Meta Data [90_Meta (Quarantine Zone)]
            A[Attachments<br/>Images/PDFs]
            T[Templates<br/>Obsidian UI]
        end
        D90 --- Meta Data
    end
    
    style D90 fill:#333,stroke:#000,stroke-width:2px,color:#fff;
    style Meta Data fill:#e2e2e2,stroke:#666,stroke-width:1px,color:#000;
```

## Consequences

### Positive
*   Vaultのセマンティック領域（`00`〜`50`）が100%純粋なテキスト空間となり、Agentのコンテキスト汚染（Context Pollution）やハルシネーションのリスクが極小化される。
*   実行ロジックがVaultから完全に排除され、データ層（Knowledge Vault）と実行層（Agent OS）の境界が明確になる。

### Negative
*   Agentの "Distill or Delete" スキルに対して、Markdownテキストのパースだけでなく「参照関係をグラフ化して孤立画像を検知・削除する（Orphaned Attachments GC）」という高度な実装要件が追加される。
