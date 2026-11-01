---
type: epic
status: in_progress
created: "2026-10-31"
updated: "2026-10-31"
tags: [AgenticOS, Organization, Sandbox, IssueManagement]
---

# Epic: Agent Company Architecture (You_Inc 組織・実行基盤の再設計)

## 📖 Background (背景と課題)
現在の `you_inc` は「憲法（`GEMINI.md`）」「図書館（`second-brain`）」「機能工場（`core-service`）」「司令塔（`agent-core`）」の骨格が整っているが、複数のAgentが「会社組織（社長 ⇄ 秘書 ⇄ チームリーダー ⇄ メンバー）」として自律協働するための課題管理（Issue）・隔離実行環境（Sandbox / Worktree）・経験蓄積の仕組みが未確立である。

## 🎯 Goal (目的: WHY)
1. **意思決定への集中**: 社長（人間）は「秘書との対話」と「エスカレーションされた未決事項の解消（判断）」のみに集中できる状態を作る。
2. **安全な並列稼働**: Agentチームがホスト環境や本流ブランチを汚染せず、独立したサンドボックス（`git worktree` 等）で安全に試行錯誤できる基盤を作る。
3. **複利的な組織学習**: SKILL（手順）は薄く保ちつつ、Agentの作業記録・失敗・学びを蓄積して組織全体の能力を継続的に引き上げる。

## 🚧 Scope (検討スコープ: WHAT)
1. **組織・通信トポロジー**: 社長 ⇄ 秘書 ⇄ チームリーダー（Orchestrator） ⇄ メンバー（Worker）の階層と介入プロトコル
2. **課題・タスク管理 (SoR)**: Agent向けIssue管理（GitHub Issues / Linear / Jira / DB）と社長個人のタスク管理（Mobile Vault / SQLite）の境界
3. **サンドボックス＆Git運用**: ワークスペース構造、`git worktree` の配置、リポジトリごとのブランチ保護・PR運用ルール
4. **組織記憶と学習ループ**: 「薄いSKILL × 厚い学び（Lessons Learned / Sense Making）」の蓄積・参照アーキテクチャ

## ✅ DoD (完了条件)
- WHY / WHAT / HOW の3段階でアーキテクチャ合意（`docs/00_Architecture_Discussion.md` への明文化）が完了していること。
- 既存の `backlog/agent_harness_construction.md` との統合・ロードマップ策定が完了していること。
- 合意したアーキテクチャに基づく Phase 1（最小構成の秘書・チームリーダー・Worktree運用）の仕様書（`spec.md` / ルール更新案）が定義されていること。

## 🧭 Routing (詳細情報のポインタ)
- **設計議論・意思決定ログ (SSOT)**: [00_Architecture_Discussion.md](file:///Users/shoheihasegawa/you_inc/agent-core/workspaces/agent_company_architecture/docs/00_Architecture_Discussion.md)
- **現在地・ワーキングメモリ (RAM)**: [context.md](file:///Users/shoheihasegawa/you_inc/agent-core/workspaces/agent_company_architecture/tasks/context.md)
- **進行管理チェックリスト (HDD)**: [progress.md](file:///Users/shoheihasegawa/you_inc/agent-core/workspaces/agent_company_architecture/tasks/progress.md)
- **関連バックログ**: [agent_harness_construction.md](file:///Users/shoheihasegawa/you_inc/agent-core/backlog/agent_harness_construction.md)
