# Open Items (未決事項・課題の洗い出し)

## 1. 「私とAgentたちの会社 (You, Inc.)」メタファーにおける拡張性と課題
- **拡張性**: 
  - `agent-os` を「本社」と見立てることで、部署（CEO, CFO, COO）ごとにエージェントを追加するだけの高いスケーラビリティを持つ。
- ~~**課題A（エージェント間通信プロトコル）**~~: [Closed by ADR-0019]
  - 非同期なファイルキューとDI（依存性注入）による疎結合プロトコルにて解決。
- ~~**課題B（ガバナンスとHuman-in-the-loop）**~~: [Closed by ADR-0010]
  - 物理的破壊を防ぐDockerサンドボックスと、コアルール変更時の社長レビュー（PRベース）必須化により解決。
- ~~**課題C（文脈・記憶の共有）**~~: [Closed by ADR-0007]
  - 全Agentが起動時に `20_Areas` からルールをJITで読み込むアーキテクチャとしたため、NotebookLM非依存で解決。

## 2. 既存ディレクトリの処理方針 (Closed)
- `ai-learning` -> 廃止・削除で合意。
- `daily-tools` -> `life-automation`（汎用ツール）と `agent-os`（実行バッチ）へ振り分け後、合意のもと廃止。

## 3. 実行層（OS）と知識層（Vault）の物理的分離に伴う未決事項
- ~~**課題D（`.agent/memory` の所属先）**~~: [Closed by ADR-0002]
  - Agentのセッション間記憶はオーケストレーション層である `agent-core` に所属することで決定。
- ~~**課題E（20_Areasのテンプレート定義の具体化）**~~: [Closed by ADR-0007]
  - `20_Areas` をガバナンスエンジン（システムプロンプトのソースコード）と位置づけ、1ファイル1テーマでWhyを併記するフォーマットで決定。
- ~~**課題F（Area間の依存関係）**~~: [Closed by ADR-0007]
  - Agentの実行開始時に必要なマイクロポリシーをピンポイントで動的ロードする（RAG的インジェクト）ことで解決。

## 4. アーキテクチャ移行に伴う新規の未決事項・要件 (New)
- ~~**課題G（統合ダッシュボードの仕様）**~~: [Closed]
  - ObsidianのDataviewプラグインを活用し、UI/View層として十分担保できると判断し解決。
- ~~**課題H（NotebookLMのRAGクエリ代替案）**~~: [Closed by ADR-0007]
  - AreaのMarkdownをAgent自身が直接ロードする方式にしたため、外部RAGシステム構築の必要性が消滅して回避。
- ~~**課題I（WIP制限ブロック機構の具体化）**~~: [Closed]
  - `agent-core` 側での `make workspace` コマンドによりシステム的に作業ディレクトリ生成を管理・制限することで解決。
- ~~**課題J（Quality Gate / Safe Delete FlowのUI）**~~: [Closed by ADR-0010]
  - サンドボックス内で作業させ、「GitHubのPull Requestを人間に投げる」こと自体が標準のUIとなるため回避。
- ~~**課題K（移行スクリプトの開発）**~~: [Moved to Task]
  - アーキテクチャの未決事項ではなく「実装タスク」であるため、移行フェーズのTODOへ移動。
- ~~**課題L（イベント検知とコンフリクト保護トランザクション）**~~: [Closed by ADR-0019]
  - `_processing/` (queue) へのアトミックな `mv` と冪等性担保により保護解決。
- ~~**課題M（NotebookLMへの自動/手動Syncフロー）**~~: [Closed by ADR-0007]
  - 課題C・Hと同様、Agentが直接Markdownを参照する仕様にしたため、NotebookLMへの同期遅延等に縛られる必要がなくなり回避。
- ~~**課題N（WIP制限のシステム的担保コマンド）**~~: [Closed]
  - `agent-core` 内で作業用ディレクトリ（git worktree）を生成する際、必ず `make workspace` コマンドを通す仕様とし、そこでWIP上限をバリデーションする仕組みにて解決。

## 5. Agent駆動運用の動的フローに関する未決事項 (New)
- ~~**課題O（PRリジェクト・CI失敗時の自律復旧フロー）**~~: [Closed by ADR-0020]
  - Day 1戦略として深追いせず、最大3回のリトライ後HITL（社長へフォールバック）で解決。
- ~~**課題P（Direct Push前のローカルLint制約）**~~: [Closed by ADR-0020]
  - `pre-commit` フックでのAuto-fix強制およびDirect Pushの禁止（Auto-Merge化）で解決。
- ~~**課題Q（`git worktree` マウントの隔離ポリシーとTeardown責務）**~~: [Closed by ADR-0010]
  - ホスト直ではなくDockerコンテナでマウント実行させることで安全性を担保し解決。
- ~~**課題R（マージコンフリクトの自律解決フロー）**~~: [Closed by ADR-0020]
  - これもDay 1戦略として複雑なコンフリクトは自律解決せず、HITLで安全に保護。
