# Agentic OS Rule Investigation Report

## 1. 認知負荷と構造的欠陥 (MUSTレベルの負債)

### A. JIT Routingとマニュアルファイル読み込みの強制 (Fatigue & Context Waste)
- **問題点**: `GEMINI.md` や `AGENT.md` において、「タスク着手時は必ず `AGENT.md` と `SKILL.md` を読み込め」「必ず `session-manager/SKILL.md` をロードせよ」といった指示が多発している。
- **MUSTレベルの理由**: LLMに対して「能動的に別のルールファイルを読みにいくこと」を求めるSoft Constraint（お願い）は、コンテキストウィンドウの無駄遣いであり、ツールコールのステップを消費させる。Agentがファイル読み込みを忘れた（あるいは読み飛ばした）時点でルールが完全にバイパスされてしまう構造的欠陥（Fatal Flaw）である。
- **改善案**: Systemic Enforcement (Hard Constraint) への移行。ワークスペースやディレクトリのコンテキスト（`AGENT.md` や `SKILL.md`）は、Agentのプロンプトにシステム側（MCPや起動スクリプト）が動的にインジェクト（Eager Load）すべきであり、Agent自身にファイルを探して読ませるべきではない。

### B. 進捗管理の自己責任化 (`progress.md` の手動更新)
- **問題点**: `AGENT.md` の `<progress_tracking>` において、Agent自身に `progress.md` や `task.md` のチェックボックスを手動で更新するよう求めている。
- **MUSTレベルの理由**: Markdownファイルの手動編集によるステート管理は、Diffの適用ミスやJSON破損のリスクを高める。また「どこまで終わったか」を毎回自己記述させるのはAgentの認知負荷が極めて高く、本来のタスクから逸脱する。
- **改善案**: Subtraction（引き算）が必要。Markdownでの自己トラッキングを廃止し、システム側でタスク管理ツール（例えば専用のタスクステータス更新APIや、Gitコミットログによる復帰）を用意し、ステート管理を外部化・自動化する。

### C. 過剰なオーケストレーションと多重防衛線の手動実行
- **問題点**: `AGENT.md` の `<governance>` にて、「影響範囲の事前分析」および「`global-alignment-reviewer` と `compliance-reviewer` によるダブルレビュー」を必須ハードゲートとしてAgent自身に実行・オーケストレーションさせている。
- **MUSTレベルの理由**: Agent自身に複雑なCI/CDパイプラインのような多重レビュープロセスを手動で回させるのは非現実的であり、高確率で無視される。ルール上は「必須ハードゲート」と呼んでいるが、実装上はAgentの良心に依存したSoft Constraintに過ぎない。
- **改善案**: これらのレビューはAgentの裁量から取り上げ、Gitのpre-commitフックやPR作成時のCI/CDシステム、またはシステムレベルのイベントとして自動発火させる（Hard Constraint）。Agentは「コードを書いて完了報告するだけ」に認知を絞る。

## 2. ルールの重複・矛盾によるノイズ

- **問題点**: `GEMINI.md` で「Zero-Shot Executionの禁止（目的アライメント）」や「コンテキスト純度の原則」が定義されているにも関わらず、`AGENT.md` の `<domain_value>` で再度同じ内容（Proposal-Driven, Context Purity）が繰り返されている。
- **改善案**: レイヤー間の責務分離の徹底。Layer 1 (`GEMINI.md`) に普遍的な振る舞いや哲学を定義したなら、Layer 2 (`AGENT.md`) からは完全に削除（Subtraction）する。重複はAgentに「どちらが優先か」という無駄な推論を強いるため避ける。

## 3. Soft Constraint (お願い) から Hard Constraint (システム制約) にすべき項目

- **Git & Shellの安全装置**: `GEMINI.md` の「エラー時即時停止(`set -e`)させよ」は、Agentにシェルスクリプトの書き方を気遣わせるのではなく、`run_command` ツールの実行環境レベルでデフォルトで適用すべき。
- **Handoff時の検証**: `AGENT.md` で `make check-all` をパスすることをセッション終了の絶対条件としているが、Agentが実行せずに終了宣言をしてしまえばすり抜けられる。終了ツール（完了報告）の内部でシステム側が `make check-all` を自動実行し、失敗したらAgentに差し戻す仕組み（Hard Gate）にする必要がある。
- **Timeless SSOT (ドキュメントとコードの同時更新)**: 「必ず同時に更新せよ」と呼びかけるだけでは不十分。コードの変更差分から関連ドキュメントの更新漏れを検知するLinterなど、システム側からのフィードバックループ（エラーリフレクション）を導入することで認知負荷を下げる。
