---
type: epic
status: in_progress
created: "2026-07-31"
updated: "2026-07-31"
tags: [ABC目標, タスク自動化]
---

# Epic 06: Corporate Goal Integration

## 📖 Background (背景と課題)
会社の人事評価である「ABC目標」と、You_Incとしての成長ドメイン（10_Areas）が分離していると、リソースが分散しパフォーマンスが低下する。
ABC目標をYou_IncのEpicとして統合・管理し、日々のスケジューリング（Briefing）や月末のエビデンス提出までを完全に自動化・仕組み化する必要がある。

## 🎯 Goal (目的)
会社のABC目標とYou_Incの10_Areas（成長）を統合し、タスクの進捗管理とエビデンス作成を自動化する。

## 🚧 Scope (やらないこと・境界)
既存の「Action Reflection Pipeline（タスク管理自動化）」のOS基盤自体は変更しない。
あくまでその基盤の上に乗る「業務アプリ・運用フロー」として構築する。

## ✅ DoD (完了条件)
- 目標設定スキル（`abc-goal-planner`）が完成し、半期の目標がSSOTに出力されていること。
- 目標がTask Registryに一括登録される仕組みができていること。
- 月末のエビデンス作成処理がバッチ化され、自動出力されること。

## 🛡️ 【必須】開発・実装の制約と前提知識 (TO-BE Architecture)
このEpicに紐づく機能開発を行うAgent（Implementer等）は、以下のルールを絶対に遵守せよ。
1. **全体アーキテクチャの把握**: 実装前に必ず `agent-core/docs/architecture/` 配下のシステム構成図とデータフロー図を参照し、全体のデータの流れ（TO-BE）を理解すること。
2. **責務の分離**: ドメインロジック（ビジネスルール）は必ず `core-service` リポジトリ内に実装せよ。APIの呼び出しやバッチの起動などの「運用スクリプト」のみを `agent-core` に配置せよ。
3. **AI防衛網の突破**: `core-service` での実装時は、TDD（テスト駆動）と Feature-Driven Packaging を遵守し、`make check-all` (Linter通過およびカバレッジ90%以上) を必ず達成せよ。

## 🧭 Routing (詳細情報のポインタ)
本Epicのすべての設計議論、決定事項、および日々のTODO進捗は以下のワークスペースで管理されています。
AIエージェントは必ず以下のワークスペースに移動して作業を行ってください。

👉 **[Workspace: corporate_goal_integration](file:///Users/shoheihasegawa/you_inc/agent-core/workspaces/corporate_goal_integration/_index.md)**

