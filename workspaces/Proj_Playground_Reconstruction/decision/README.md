# Architecture Decision Records (ADR)

本ディレクトリは、「You, Inc.」アーキテクチャの根幹となる意思決定の履歴（なぜそのように決定したか）を記録・蓄積する場所です。
未来のAgentや開発者が「なぜこのような設計になっているのか？」と疑問に思った際は、ここを参照してください。

> [!IMPORTANT]
> - 本ディレクトリのファイルは純粋なADRフォーマット（Context / Decision / Consequences）に従う必要があります。単なる古い仕様書の丸投げは禁止されます。
> - 最新の `to-be/` と完全に矛盾する過去の決定は、`Status: Deprecated` ラベルを付与してアーカイブ扱いとしています。

## 🟢 有効なADR (Active)

| ID | Title | Summary |
|---|---|---|
| 0002 | [Agent Orchestration Layer](./0002_agent_orchestration_layer.md) | `agent-core` の新設による関心の完全な分離 |
| 0003 | [Physical Separation of Capture Zone](./0003_physical_separation_of_capture_zone.md) | iCloudのInbox分離と清書AgentによるYAML化の強制 |
| 0004 | [Progressive Migration Strategy](./0004_progressive_migration_strategy.md) | 新DBへの段階的なデータクレンジングと移行 |
| 0005 | [Decouple Projects and Vault](./0005_decouple_projects_and_vault.md) | `10_Projects` の廃止と `agent-core` への実行状態の委譲 |
| 0006 | [Source Compiled Knowledge Architecture](./0006_source_compiled_knowledge_architecture.md) | `40_Permanent_Notes` のフラット化と RAG への提供 |
| 0007 | [Redefine Areas as Governance Engine](./0007_redefine_areas_as_governance_engine.md) | `20_Areas` をシステムガバナンスのエンジンとして再定義 |
| 0008 | [Abolish Archives & Adopt Distill-or-Delete](./0008_abolish_archives_and_adopt_distill_or_delete.md) | ゴミ箱化を防ぐ「蒸留するか削除するか」の強制フロー |
| 0009 | [Define 90_Meta Architecture](./0009_define_90_meta_architecture.md) | `90_Meta` を非セマンティックデータの隔離領域（RAG対象外）として定義 |
| 0010 | [Agent Harness and Sandbox Strategy](./0010_agent_harness_and_sandbox_strategy.md) | `agent-core` におけるDockerサンドボックスとDIによる破壊防止 |
| 0011 | [Agent Context Routing Strategy](./0011_agent_context_routing_strategy.md) | READMEを用いたルールの遅延ロード（JIT）とコンテキスト節約 |
| 0013 | [Architecture Review Guidelines](./0013_architecture_review_guidelines.md) | 3大リポジトリ（second-brain/core-service/agent-core）のレビュー観点 |
| 0014 | [Mobile Integration Concept](./0014_mobile_integration_concept.md) | モバイルを純粋なInput/View層（Thin Client）として扱う概念 |
| 0016 | [Project Workspace Lifecycle](./0016_project_workspace_lifecycle.md) | `agent-core/workspaces` での実行とPermanent Notesへの収穫フロー |

## ⚠️ 廃止されたADR (Deprecated)

過去の過渡期に作成されたものの、最新の `to-be/` アーキテクチャに完全に統合・置換されたため、現在は無効となっている決定事項です。

| ID | Title | Reason for Deprecation |
|---|---|---|
| 0001 | [Project Kickoff](./0001_project_kickoff.md) | 単なるキックオフメモであり恒久的なADRではないため |
| 0015 | [Data Governance Concept](./0015_data_governance_concept.md) | 古い仕様書フォーマットであり、最新のディレクトリ名（`40_Permanent_Notes`等）と矛盾するため |
| 0017 | [Knowledge Build Pipeline](./0017_knowledge_build_pipeline.md) | 古い仕様書の丸投げであり、最新の3層分離設計と矛盾するため |

---
*(Note: 0012, 0018 は完全な古い仕様書の丸投げ（ノイズ）であったため削除されました)*
