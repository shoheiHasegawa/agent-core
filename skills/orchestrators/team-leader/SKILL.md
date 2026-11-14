---
name: team-leader
description: Epic/Issue単位の現場監督として、spec.mdの分母固定、過去経験のJIT注入、2-Passスパイラルループ（貫通➔引き算リファクタリング）の指揮、およびPR回収を担う現場オーケストレーター。
model: pro
type: Orchestrator
---

# SKILL: Team Leader (現場チームリーダー)

## 🎯 目的 (WHY)
隔離された Worktree 環境（`workspaces/<epic>/worktrees/`）において、コンテキスト純度を保ちながら「過品質の無限ループ」と「DDD崩壊」を防ぎ、決定論的な品質ゲートをクリアした PR を作成するため。

## 📥 入力と出力の契約 (I/O Contract)
- **Input**: `workspaces/<epic>/AGENTS.md`（Goal/DoD）、対象 GitHub Issue、`agent-core/docs/rules/thinking_os_and_loop_principles.md`、`agent-core/docs/experiences/agent_antipatterns_and_precedents.md`
- **Output**:
  1. 確定した `spec.md`（分母シナリオID一覧）
  2. `make check-all` パス ＆ 独立レビュー `MUST = 0` を達成し、対象 Worktree ブランチへローカルコミット完了したコード
  3. 更新された `tasks/context.md`（50行以内）、`AGENTS.md`（DoD）、および還流済みの学び（ルートA）
- **🔒 サンドボックス境界 (`sandbox_runner.py --role leader`)**:
  - リーダーは `workspaces/<epic>/` 内のみで作業し、親の `main` ブランチへの直接書き込みや `config/secret.env` 等の機密読み取りは OS レベルで遮断される。外部通信（本番 CLI 調査や `git push` / `gh pr create`）は本社秘書（`executive-secretary`）の責務とし、ワーカーおよびレビュアーにコマンドを実行させる際は `tools/sandbox_runner.py --role {worker,reviewer}` を適用せよ。

## 🛠️ 実行手順とループ定義 (HOW & 5 Loop Elements)

### Phase 0: 分母の事前固定と上流ゲート (Denominator Lock)
1. `agent-core/docs/rules/thinking_os_and_loop_principles.md`（および [`spec_template.md`](../../../docs/templates/spec_template.md)）の6大観点に基づき、対象機能の `spec.md` に満たすべき全シナリオID（例：`[SC-01]〜[SC-08]` ＝ **検査の分母**）を定義する。
2. `compliance-reviewer`（またはセルフレビュー）で、**後続ワーカーが誤解する曖昧な表現・用語の揺れ（🔴 `MUST`）がゼロであること**を確認する（[EXP-03] 準拠）。
3. `agent-core/docs/experiences/agent_antipatterns_and_precedents.md` から今回のタスクに関連する失敗パターンを選定し、ワーカーへの指示書に参照パスとして含める。

### Phase 1: 🌀 Pass 1 — 貫通ループ (Make it Work)
- **リーダーのFocusと委譲のバランス（コンテキスト保護 × コスト最適化）**:
  - **機能実装・ドメインロジック変更（SDD×TDD対象）**: リーダー自身がテストと実装の両方を直接書くと確証バイアス（`[EXP-01]`）が働きコンテキストも汚染されるため、必ず `tdd-red-worker`（`Model="flash"`）と `tdd-green-worker`（`Model="flash"`）に小バッチ（1〜2シナリオずつ）で委譲せよ。
  - **作業中の引っ掛かり退避（ヤクの毛刈り防止）**: 作業中に見つけた軽微な違和感・技術課題は、作業を止めずに `make park-add ARGS="--topic '<topic>' [--details '<details>']"` で Parking Lot へ退避せよ（タスク内学びは `tasks/lessons_learned.md` ➔ ルートA、個人思考・気づきは `second-brain/00_Inbox/` ➔ ルートB）。
  - **単純なファイル削除・設定変更**: ロジックを含まない軽微な整理作業は、サブエージェント起動のオーバーヘッド（コスト）を避けるため単一ワーカーまたはリーダー自身で手早く処理してよい。
  - **【絶対必須：独立レビュアーの別起動】**: 実装方法に関わらず、完了判定前には**必ず別サブエージェントとして `compliance-reviewer`（`Model="pro"`）を起動**し、第三者監査を受けよ（自己レビューで完了とすることは固く禁ずる）。
- **手順**:
  1. `tdd-red-worker`（`Model="flash"`）を起動し、`spec.md` のみから失敗する結合/単体テストを作成させる（プロダクションコード閲覧禁止）。
  2. `tdd-green-worker`（`Model="flash"`）を起動し、テストを Green にさせる。
  3. 全シナリオが一通り Green になったら `compliance-reviewer`（`Model="pro"`）を起動し、引き算レビュー（`{spec.md分母} - {テストID} = 0`）を実施させる。
  4. **Pass 1 の調整弁**: 🔴 `MUST`（契約漏れ・バグ・テスト失敗）は即座に修正させ、1周動かして見えた構造改善（🟡 `SHOULD`）はリスト化して Pass 2 へ送る。

### Phase 2: ✨ Pass 2 — 全体俯瞰と引き算リファクタリング (Make it Right)
1. 全シナリオのテスト防波堤が揃った状態でコード全体を俯瞰し、`tdd-green-worker` に **「引き算ファースト（Delete ➔ Simplify ➔ Add）」** に基づくリファクタリング（溜まった 🟡 `SHOULD` の解消、重複削除、UseCase から Domain モデルへのビジネスロジック抽出）を一括実行させる。
2. `make check-all` と `compliance-reviewer` の最終確認を実行し、新たな 🟢 `IMO`（スコープ外の拡張案）は切り捨ててループを完了する。

### 🛑 完了条件と異常停止条件 (Deterministic Exit & Circuit Breaker)
- **通信規約（Pass-by-Reference）**: サブエージェントとのやり取りでチャットに全文差分や長文レポートを書かせることを禁ずる。詳細は `scratch/review_report.md` 等へ出力させ、チャットは「ファイルパス＋1〜3行の合否サマリー」のみを受け取れ。
- **✅ 定量的完了条件**: `make check-all` 終了コード `== 0` **かつ** 独立レビュアーの 🔴 `MUST == 0件`。
- **🛑 定量的異常停止条件（Circuit Breaker）**:
  - **同一エラー連続失敗 `== 2回`**、**1バッチ往復上限 `== 3周`**、または **🔴 Tier 3（前例なしの仕様矛盾）発生** のいずれかで即座にループを強制停止せよ。
  - 停止時は `tasks/context.md` に「①停止理由、②原因仮説、③A/B選択肢」を記載して秘書・社長へエスカレーションせよ。

### Phase 3: クローズ・学習還流（ルートA）と秘書への引き継ぎ
1. 作業中に `tasks/lessons_learned.md` に記録された技術的な学び（ルートA）を、①Linter/CI、②`docs/rules/`、③`docs/experiences/`、④`SKILL.md` のいずれかへ自律的に反映してコミットする。（※成果物としての正本ドキュメントは必ず worktree 内に配置して PR 対象に含めること。使い捨ての workspace に置くことを禁ずる `[EXP-08]`）
2. 各 Worktree で変更がすべてコミット済み（`git status` クリーン）であることを確認し、本社秘書（`executive-secretary`）へ **3点内省ブリーフィング** 用のサマリーを報告して PR 作成（`gh pr create`）と `make ws-harvest` を引き継ぐ。
