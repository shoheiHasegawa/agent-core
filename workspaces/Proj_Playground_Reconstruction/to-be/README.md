# You, Inc. TO-BE Architecture

本ディレクトリ（`to-be/`）には、You, Inc. の最新のアーキテクチャ設計書（SSOT）が格納されています。
システムの全体像や各リポジトリの詳細については、以下のドキュメントを参照してください。

## 🗺️ アーキテクチャ・マップ

1. **[00_overall_architecture.md](./00_overall_architecture.md)**
   - **必読**: システムの全体像（You, Inc.のメタファー）、3大リポジトリの構成、およびデータライフサイクルのフロー図。
2. **[10_agent-core_architecture.md](./10_agent-core_architecture.md)**
   - `agent-core`（会社の現場・オフィス）の詳細設計。Agentの隔離作業環境やWorkflowの仕組み。
3. **[11_agent-core_operational_flow.md](./11_agent-core_operational_flow.md)**
   - Agentの動的な運用フロー（無限ループ防止、コンフリクト解消、WIP制限、教訓抽出タイミング等）。
4. **[20_second-brain_architecture.md](./20_second-brain_architecture.md)**
   - `second-brain`（知識体系・Permanent Notes）の詳細設計。
5. **[30_core-service_architecture.md](./30_core-service_architecture.md)**
   - `core-service`（情報システム部・道具箱）の詳細設計。副作用のService化、DIの仕組み、厳格な品質ゲート。

> [!NOTE]
> 過去の設計セッションの記録（過渡期のドキュメント 01〜07 等）はすべて `../decision/` に退避（ADR化）されています。設計の背景（Why）を知りたい場合はそちらを参照してください。
