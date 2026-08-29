# Context Engineering 調査レポート: MUSTレベルの負債

`agent-core/GEMINI.md`, `agent-core/AGENT.md`, および `agent-core/docs/` のドキュメント群を Context Engineering の観点から分析した結果、コンテキストウィンドウの枯渇や JIT ルーティングの失敗に直結する「MUSTレベルのアーキテクチャ負債」が複数特定されました。

## 1. `AGENT.md` の責務違反とコンテキスト重複（Memory Context Waste & Overload）
- **事象**: 
  - `AGENT.md` は本来「ドメインミッションと関連ルールへのポインタ（ルーティング）」に徹するべきであると `document_architecture_principles.md` (2.2) で規定されています。
  - しかし、現在の `agent-core/AGENT.md` には、`GEMINI.md` と重複する普遍的ルール（Proposal-Driven / Zero-Shotの禁止、Context Purityなど）が記述されています。
  - さらに、`<execution_flow>` や `<governance>` ブロックに、Quality Gateの詳細や Handoff プロトコルなど、具体的な手順が直接ハードコードされており、著しいFat化（約60行に及ぶ重厚なルール）を引き起こしています。
- **負債のインパクト**: 
  - すべてのタスクの初動で読み込まれる `AGENT.md` が肥大化することで、LLMのワーキングメモリ（コンテキストウィンドウ）を無駄に消費し、Information Overloadによる Lost in the middle（指示忘れ）を誘発します。
- **解決策**:
  - `AGENT.md` から `GEMINI.md` との重複を削除する。
  - 実行フローやガバナンスの詳細なルールは `docs/rules/system_heuristics.md` や `orchestration.md` に切り出し、`AGENT.md` は純粋な静的リンク（ポインタ）のみにダイエットさせる。

## 2. JIT ルーティングの矛盾と動的DI (Directory Search) の残存（JIT Routing Failures）
- **事象**:
  - `document_architecture_principles.md` (3.1) では、「推論リソース温存と確実性担保のため、実務や標準オーケストレーションにおける `_index.md` からのクエリ抽出（動的DI）は廃止し、**すべて静的DI（ファイル直接リンク）とする**」と明記されています。
  - しかし、`AGENT.md` の `<jit_routing>` には `core-service/docs/rules/` や `agent-core/docs/architecture/` のような「ディレクトリパス」が指定されており、Agentにディレクトリ探索（ls）を強要しています。
  - また、`AGENT.md` の `<governance>` および `workspace_management.md` には、廃止されたはずの「`_index.md` をエントリーポイントとしたルーティング」の指示が依然として残っています。
- **負債のインパクト**: 
  - 静的DI（ファイルパス直接指定）がなされていないため、Agentが対象ファイルを特定するのに余分なツール呼び出し（`list_dir` 等）を行い、推論リソースを浪費します。また、探索の失敗によるコンテキスト欠落リスクが生じます。
- **解決策**:
  - `AGENT.md` の JIT ルーティングリストを、ディレクトリパスではなく、具体的なMarkdownファイルへの絶対（または相対）直接リンク（静的DI）に書き換える。
  - `_index.md` によるルーティングの記述を完全に廃止し、ルールに一貫性を持たせる。

## 3. Workerへの不要なアーキテクチャ情報の露出（Information Overload）
- **事象**:
  - `document_architecture_principles.md` によると、Tier 2（Worker）の純粋な実装フェーズにおいては、「大局的な思想背景（`docs/architecture/`）はコンテキスト過多となるため読み込まない」と規定されています。
  - しかし、現状のシステムでは `AGENT.md` にすべてのポインタがフラットに記載されているため、実装担当のWorkerが不要なアーキテクチャ文書へアクセスしやすくなっており、認知負荷を上げています。
- **負債のインパクト**: 
  - Workerスキル（単一責任の実行者）が深いコンテキスト（WHY/WHAT）を読み込むことで、手段の目的化や過剰な推論（Zettelkastenとの境界線違反）を招く原因となります。
- **解決策**:
  - SKILL（ワーカー用手順）自体に、必要な `docs/rules/*.md` のみを直接静的DIする設計（`skill_design_principles.md` に準拠）を徹底し、`AGENT.md` 側からは大局のアーキテクチャ（Orchestrator向け）とルール（Worker向け）のポインタを明確に分離する。
