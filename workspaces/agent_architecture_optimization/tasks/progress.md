# Epic Workspace Progress (SSOT)

**【メタデータ】**
- Epic: `agent_architecture_optimization`
- 種別: `[アーキテクチャ最適化・リファクタリング]`
- 現在地: `[Phase 3: 実装中]` ➔ `[PR 5: ドキュメント整理・レガシー移行]`
- 次回アクション: PR 5 レガシー移行と空スタブ清掃の委譲

---

## 📋 タスク進捗チェックリスト

### Phase 1: 課題の洗い出しと記録 (Discovery & Problem Definition)
- [x] コンテキスト効率・キュー残骸・パス不整合の課題特定
- [x] `queue/` 完全撤廃方針（Zero-Queue Architecture）の採用決定・記録
- [x] ループエンジニアリング・モデル選択（Pro一律継承）の課題特定
- [x] ハーネスエンジニアリング・プロンプト重複・空ファイル・パスハック残存の課題特定
- [x] 課題正本ドキュメント (`docs/00_Identified_Issues_and_Challenges.md`) の更新

### Phase 2: 局所最適を避けた全体最適のための改善案の議論 (Holistic Architecture Design)
- [x] 1. Cluster 1 確定: State & Lifecycle (`docs/01_Cluster1_State_and_Lifecycle_Design.md`)
- [x] 2. Cluster 2 確定: Model Matrix & Loop Engineering (`docs/02_Cluster2_Model_Matrix_and_Loop_Engineering.md`)
- [x] 3. Cluster 3 確定: Prompt Purity & Rule Leanization (`docs/03_Cluster3_Prompt_Purity_and_Rule_Leanization.md`)
- [x] 4. 全体最適化レビューの実施とフィードバック反映（Error Event Bus 採用 & 全18スキル改修仕様 `docs/04_Skill_Refactoring_Matrix_and_High_Value_Specs.md` 確定）

### Phase 3: 対策の実装と検証 (Implementation & Verification - Atomic PR Cycles)
- [x] **PR 1: Event Bus 移行 & DI/設定層の整合**
  - [x] `agent-core/app_context.py` & `config/conf.env` のイベントパス設定化
  - [x] `core-service/src/di/config.py`, `container.py` のDI注入先更新
  - [x] `core-service/src/infrastructure/local_file/queue_system_event_gateway.py` の投函先を `events/` に是正
  - [x] `agent-core/docs/architecture/data_flow.md` の更新
- [x] **PR 2: クリーンネス自動検証ハーネスの構築**
  - [x] `agent-core/tools/verify_cleanliness.py` の実装（50行制限、ゴミ検知、パス構造検証）
  - [x] `agent-core/scripts/pre_handoff_verify.sh` & `Makefile` & `AGENT.md` への統合
- [x] **PR 3: サブエージェント契約テンプレートの作成**
  - [x] `agent-core/templates/Subagent_Prompt_Template.md` の作成（契約型Few-Shot）
  - [x] `templates/README.md` & `AGENT.md` & `workspace_management.md` への参照登録
- [x] **PR 4: 全18スキルのリファクタリング (高付加価値化 & ルール純度向上)**
  - [x] Category A (対話7スキル): `night-routine`, `inbox-triage`, `journaling-counselor`, `priority-planner`, `johari-profiler`, `socratic-interviewer`, `sdd-spec-writer`
  - [x] Category B (重ワーカー4スキル): `tdd-green-refactorer`, `tool-architect`, `skill-architect`, `skill-reviewer`
  - [x] Category C (軽ワーカー4スキル): `tdd-red-coder`, `compliance-reviewer`, `zk-formatter-qa`, `workspace-architect`
  - [x] Category D (オーケストレーター3スキル): `session-manager`, `sdd-loop-orchestrator`, `zk-distillation-orchestrator`
- [ ] **PR 5: ドキュメント整理・レガシー移行**
  - [ ] 空スタブファイル削除 (`core-service/docs/rules/api_gateway.md` 等)
  - [ ] 既存ワークスペース（`ai_study_sessions`, `systematic_trading` 等）の `tasks/` 構造への移行
  - [ ] 旧 `agent-core/queue/` の完全削除
- [ ] **PR 6: 全体品質検証とコミット**
  - [ ] `pre_handoff_verify.sh` & `make check-all` パス検証
  - [ ] Git commit & push

---

## 💡 Session Insights (未登録の教訓・知見)
- `[ ]` **Zero-Queue & Backlog-Workspace Separation**: 企画（`backlog/`）と作業現場（`workspaces/`）をライフサイクルで明確に分離し、中間のキューを排除することで、コンテキストの純度と探索速度が劇的に向上する。
- `[ ]` **Event Bus vs Task Handoff**: セッション引き継ぎとシステム非同期エラー通知は別物。引き継ぎはRAM/HDDで完結させ、システムエラー通知のみを極小のEvent Bus（`events/`）に分離する。
- `[ ]` **Contract-Driven Flash Subagents**: Flash モデルは呼び出し契約（入力・制約）と報告契約（出力型）を固定することで、Pro 相当の精度と Flash の爆速・低コストを両立できる。
- `[ ]` **Rule Leanization & High-Value Prompts**: 機械的ルールをLinterに任せ、プロンプトには思考ヒューリスティクス、Few-Shot実例、エスカレーション境界を注入する。
