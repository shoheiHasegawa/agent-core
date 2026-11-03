# 🗺️ CCA-F Topic Index & Socratic Questions (出題トピック一覧)

> **💡 運用の手引き**
> - **🔴 MUST（Pass 1: 骨格貫通）**: 概念理解と設計思想の核。まずはここを優先して秘書と壁打ちし、`second-brain` にアトミックノート（社長のメガネ）を作成する。
> - **🟡 SHOULD（Pass 2: 肉付け）**: 詳細仕様・パラメータ・エッジケース。Udemy模試で間違えた（Delta）際に深掘りする。
> - **🟢 IMO（Pass 3: スコープ外）**: 試験には不要なマニアックな実装詳細。今回は深入りしない。

---

## Domain 1: Agent Architecture & Orchestration (エージェント設計・連携)

### 🔴 MUST
1. **Workflow vs Agent (決定論的パイプライン vs 自律ループ)**
   - *ソクラテスの問い*: 「なぜAnthropicは、可能な限りAgentではなく決定論的なWorkflow（Router / Chaining / Parallel）を使うことを推奨するのか？ そのトレードオフの境界線はどこにあるか？」
2. **Subagent & Context Isolation (情報隠蔽とコンテキスト純度)**
   - *ソクラテスの問い*: 「単一のエージェントに全ツールを持たせるのではなく、Subagentに委譲すべきなのはどのような状況か？ コンテキストの汚染と精度の関係は？」
3. **Agentic Loop Termination (停止条件と無限ループ防止)**
   - *ソクラテスの問い*: 「エージェントが自己判断で無限ループや堂々巡りに陥るのを防ぐために、アーキテクトが絶対に組み込むべき安全装置は何か？」

### 🟡 SHOULD
4. **Human-in-the-Loop (人間介入・承認ゲート)**
   - *ソクラテスの問い*: 「自律性と安全性のトレードオフにおいて、どのような操作（Side Effect）で人間承認を必須とすべきか？」
5. **State Handoff & Session Management**
   - *ソクラテスの問い*: 「エージェント間や複数ターンにわたるセッションで、最小限のコンテキストで状態を引き渡す設計パターンは？」

---

## Domain 2: Tool Design & MCP Integration (ツール設計 & MCP連携)

### 🔴 MUST
1. **MCP 3大プリミティブの責務分離 (Resources vs Prompts vs Tools)**
   - *ソクラテスの問い*: 「MCPにおいて、なぜデータをToolsではなくResourcesとして公開すべき場合があるのか？ それぞれのセマンティクスの違いは？」
2. **Tool Definition Best Practices (ツール定義の品質)**
   - *ソクラテスの問い*: 「モデルが正確にツールを選択・実行するために、説明文（Description）とJSON Schemaに含めるべき必須要素と、逆に含めてはいけないノイズは？」
3. **Scoped Permissions & Security Boundaries (最小権限とセキュリティ)**
   - *ソクラテスの問い*: 「外部MCPサーバーを接続する際、プロンプトインジェクションや機密流出を防ぐためのアーキテクチャ上の多層防御とは？」

### 🟡 SHOULD
4. **Tool Execution Error Handling (自己修復フィードバック)**
   - *ソクラテスの問い*: 「ツール実行が失敗した際、例外を投げてクラッシュさせるのではなく、モデルにどうエラーを返せば自己修正を促せるか？」
5. **MCP Transports (Stdio vs SSE)**
   - *ソクラテスの問い*: 「ローカルCLI統合（Stdio）と分散環境・リモート統合（Server-Sent Events: SSE）の使い分け基準は？」

---

## Domain 3: Claude Code Configuration & Workflows (Claude Code設定とCI/CD)

### 🔴 MUST
1. **CLAUDE.md Hierarchy & Rule Injection**
   - *ソクラテスの問い*: 「プロジェクトルート、サブディレクトリ、ユーザーグローバルの `CLAUDE.md` はどう解決されるか？ 指示が競合したときの優先順位は？」
2. **Permission Model & Sandbox Boundaries (実行許可とサンドボックス)**
   - *ソクラテスの問い*: 「Claude Codeが自律的にコマンドを実行する際、開発者の環境破壊を防ぐための許可フラグや承認境界はどう設計されているか？」
3. **Headless / CI/CD Automation**
   - *ソクラテスの問い*: 「人間が介在しないCI/CDパイプラインやバッチ処理でClaude Codeを安全に完結させるための設定と制約は？」

### 🟡 SHOULD
4. **Context Window Management (`/compact`, `/clear`)**
   - *ソクラテスの問い*: 「長時間の開発セッションで推論精度が低下する原因と、Claude Codeにおけるコンテキストリセットの運用基準は？」
5. **Custom Slash Commands & Subagents**
   - *ソクラテスの問い*: 「定型タスクやチーム固有の開発フローをClaude Code上で自動化・共通化するための仕組みは？」

---

## Domain 4: Prompt Engineering & Structured Output (プロンプトと構造化出力)

### 🔴 MUST
1. **XML Tags & Semantic Boundaries (構造化コンテキスト)**
   - *ソクラテスの問い*: 「なぜClaudeに対してXMLタグ（`<context>`, `<instructions>` 等）が圧倒的に有効なのか？ プロンプトインジェクション防御との関係は？」
2. **Structured Outputs & Schema Validation**
   - *ソクラテスの問い*: 「JSON出力を確実に得るために、システムプロンプトの指示、Tool Calling（API機能）、Assistant Prefillのどれを選択すべきか？」
3. **Few-Shot vs Zero-Shot Trade-offs**
   - *ソクラテスの問い*: 「Few-shot例を与えることで得られる精度向上と、トークン消費・バイアス・過学習のリスクをどう天秤にかけるか？」

### 🟡 SHOULD
4. **Assistant Message Prefilling**
   - *ソクラテスの問い*: 「Claude特有の機能である『Assistantメッセージの事前入力（Prefill）』は、どのような出力制御（JSON開始、思考強制等）に使えるか？」
5. **Thinking Mode & Chain-of-Thought (思考プロセスの制御)**
   - *ソクラテスの問い*: 「推論（Thinking）を有効化すべき問題と、無駄なレイテンシ・コストを生むだけの問題の違いは何か？」

---

## Domain 5: Context Management & Reliability (コンテキスト管理と信頼性)

### 🔴 MUST
1. **Prompt Caching Mechanics (Context Cachingの挙動)**
   - *ソクラテスの問い*: 「キャッシュヒットの条件（最小1024トークン、プレフィックス完全一致、TTL5分）を踏まえ、プロンプトの構成順序はどうあるべきか？」
2. **Uncertainty & Hallucination Mitigation (不確実性の制御)**
   - *ソクラテスの問い*: 「モデルに知ったかぶりをさせず、情報が不足している時に『分かりません』と答えさせるためのGrounding（接地）設計は？」
3. **Fallback & Graceful Degradation (障害対策)**
   - *ソクラテスの問い*: 「レートリミット（429）やプロバイダ障害が発生した際、システム全体を停止させないためのフォールバック戦略（指数バックオフ、モデルフォールバック）は？」

### 🟡 SHOULD
4. **Latency vs Cost vs Quality (3元評価とEvals)**
   - *ソクラテスの問い*: 「Claude 3.5 Sonnet / Haiku / Opus（3.7含む）を適材適所で使い分けるための評価基準と、定期的な性能退行テスト（Evals）の組み方は？」
5. **Message Batches API**
   - *ソクラテスの問い*: 「非同期・大容量データ処理において、通常APIの半額・高スループットを実現するBatches APIの制約と適用シーンは？」
