---
type: epic
status: completed
created: "2026-10-31"
updated: "2026-11-01"
tags: [AgenticOS, Organization, Sandbox, IssueManagement]
---

# Epic: Agent Company Architecture (You_Inc 組織・実行基盤の再設計)

## 📖 Background (背景と課題)
現在の `you_inc` は「憲法（`GEMINI.md`）」「図書館（`second-brain`）」「機能工場（`core-service`）」「司令塔（`agent-core`）」の骨格が整っているが、複数のAgentが「会社組織（社長 ⇄ 秘書 ⇄ チームリーダー ⇄ メンバー）」として自律協働するための課題管理（Issue）・隔離実行環境（Sandbox / Worktree）・経験蓄積の仕組みが未確立である。

## 🎯 Goal (目的: WHY)
1. **意思決定への集中と内省による成長**: 社長（人間）は「秘書との対話」「初めての未決事項の判断（Tier 3）」「3点ブリーフィングを通じた内省」に集中し、ブラックボックス化を防ぐ。
2. **安全な並列稼働**: Agentチームが本流ブランチを汚染せず、独立した `git worktree` 環境で安全に開発・検証できる基盤を作る。
3. **複利的な組織学習**: 「SKILLは薄く、思考原則は鋭く、経験（学び）は厚く」の3層構造で組織能力を複利的に引き上げる。

## 🚧 Scope (検討スコープ: WHAT)
1. **組織・通信トポロジー**: 社長 ⇄ 秘書 ⇄ チームリーダー ⇄ メンバー（TDDワーカー・独立レビュアー）の4層階層と前例ベース3段階トリアージ
2. **課題・タスク管理 (SoR)**: 会社の課題管理（GitHub Issues）と社長個人のスケジュール/ToDo（Google Calendar & Tasks + Mobile Vault）の境界
3. **サンドボックス＆Git運用**: `make ws-new` / `make ws-harvest` による `git worktree` 隔離開発と3リポジトリ独立CI
4. **組織記憶と学習ループ**: 2-Pass スパイラルループ（Pass 1: 貫通 ➔ Pass 2: 引き算リファクタリング）と2系統還流（ルートA: `agent-core` / ルートB: `second-brain`）

## ✅ DoD (完了条件)
- WHY / WHAT / HOW の3段階でアーキテクチャ合意が完了し、本流の [`docs/architecture.md`](../../docs/architecture.md) へ昇格・永続化されていること。
- 旧文書群の重複・陳腐化が一掃され、7コアSKILL・思考原則（`docs/rules/`）・経験ストック（`docs/experiences/`）へ再編されていること。
- `core-service` の DI 自己完結化（`from_env`）および公式CLI（`src/entrypoints/cli/`）が `team-leader (pro)` ➔ `tdd-red/green (flash)` ➔ `compliance-reviewer (pro)` の実サブエージェント協働で実装・検証され、`main` へ回収されていること。

## 🧭 Routing (詳細情報のポインタ)
- **全社アーキテクチャ正本 (SSOT)**: [architecture.md](../../docs/architecture.md)
- **設計議論アーカイブ**: [00_Architecture_Discussion.md](docs/00_Architecture_Discussion.md)
- **現在地・ワーキングメモリ (RAM)**: [context.md](tasks/context.md)
- **進行管理チェックリスト (HDD)**: [progress.md](tasks/progress.md)
- **学習ログ**: [lessons_learned.md](tasks/lessons_learned.md)
