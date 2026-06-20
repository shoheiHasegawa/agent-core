# ADR 0006: Source Code and Compiled Binary Model for Knowledge (Permanent Notes vs NotebookLM)

## Date
2026-06-13

## Context
従来の設計では、情報保管庫（Resources）とツェッテルカステン（Permanent）が同居しており、「フラットに繋がり拡張していくPermanent Notesの性質」と「AI（NotebookLM等）がハルシネーションを起こさず特定の文脈で機能するために必要なスコープの絞り込み」という要件が矛盾・衝突していた。また、Agentがコンテキストを読み取るにあたり、階層の深いディレクトリ構造は探索効率の悪化を招いていた。

## Decision
1. **Source Code vs Compiled Binary メタファーの採用**: ローカル（Obsidian + Git）を「ソースコード（SSOT）」とし、NotebookLM（Google Drive等）を「コンパイル済みの実行用バイナリ」として扱う。
2. **`40_Permanent_Notes` の新設と完全フラット化**: `30_Resources` 内にあった Permanent ノート群を最上位ディレクトリ `40_Permanent_Notes` に分離・昇格させる。AIによるビルド（抽出）プロセスを単純化し、純粋なコンテキストによる検索を可能にするため、この領域は**一切のサブフォルダを持たない「完全フラット構造」**とする。
3. **`30_Resources` の再定義**: `30_Resources` は「Permanent Notesの材料（生データ）」としての外部資料やトレード日誌の保管庫とし、人間が検索するための適度な階層構造（フォルダ分け）を許容する。名称についてはPARAメソッドに準拠し維持するが、役割を明確化する。
4. **知識のビルド・パイプライン構築**: ObsidianのPermanent Notes内から、YAMLフロントマターの特定のタグ（例: `#context/architecture`）を持つノートを抽出（ビルド）し、用途別のNotebookLM用ディレクトリに同期（デプロイ）する仕組みを設ける。
5. **Agentペルソナによるコンテキストのハーネス**: AntiGravity側のAgent（Architect, Traderなど）は、用途別にビルドされた専用のNotebookLMのみを「外部脳」として参照し、ハルシネーションを抑制する。

## Consequences

### Positive
*   Permanent Notes（人間の思考の広がり）と、LLMの制約（文脈の絞り込み）の構造的矛盾が完全に解消される。
*   You, Inc. の哲学や一次情報（失敗の記録など）が強制的に適用された、品質の高いAIのアウトプットが保証される。
*   Permanent Notesを完全フラット化し、フロントマターで管理することで、将来的なメタデータ主導のRAGやグラフデータベースへの移行が容易になる。

### Negative
*   ローカルとDrive間の同期・ビルドを自動化するスクリプト（Python等）の実装・維持コストが発生する。
