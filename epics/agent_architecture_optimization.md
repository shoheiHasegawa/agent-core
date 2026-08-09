---
type: epic
status: completed
created: "2026-08-08"
updated: "2026-08-08"
tags: ["architecture", "context-engineering", "agentic-os", "subagents", "performance"]
---

# Epic: Agent Architecture Optimization (コンテキスト＆ループエンジニアリング全体最適化)

## 📖 Background (背景と課題)
You_Inc システムの成長に伴い、AIエージェントの運用層（`agent-core`）において、コンテキスト効率の低下（キューの肥大化・パスの不整合・過剰読み込み）、サブエージェント起動時のモデル選択の未最適化（一律 Pro 継承によるレイテンシ・コスト増）、コールドスタート時の Eager Loading による初期負荷などの課題が顕在化している。
これらを場当たり的に局所最適化するのではなく、システム全体の統一性・スケーラビリティ・認知負荷低減の観点から全体最適としてリファクタリングする。

## 🎯 Goal (目的)
1. **コンテキスト効率の極大化**: ゴミの自律パージ、SSOTパス完全統一、Selective JIT Loadingの確立。
2. **ループエンジニアリングとモデル最適化**: サブエージェントのタスク特性に応じた最適モデルマッピング（Pro / Flash / Flash-Lite / 親Role Switching）の標準化とエスカレーション戦略の導入。
3. **最速・最小フットプリントのコールドスタート**: 3-Step Lazy Bootstrapping による即時文脈復元。

## 🚧 Scope (やらないこと・境界)
- ビジネスロジック（`core-service` 内のドメイン機能）の変更は対象外（`agent-core` の運用層・スキル・ドキュメント規約が主対象）。
- 既存の優れたアーキテクチャ原則（3-Tier, ダブルループTDD, Timeless SSOT）の根本破壊は行わず、規約の徹底と効率化に集中する。

## ✅ DoD (完了条件)
1. 課題の網羅的洗い出しと全体最適設計ドキュメントの合意。
2. 全 `SKILL.md` のモデル定義および Role Switching / Subagent 境界の整合性修正。
3. `queue/` 管理およびコールドスタート手順（`session-manager` 等）の改訂とクリーンアップ。
4. ドキュメント間のパス表記・SSOT整合性の完全一致。
5. `audit_skills.py` および `pre_handoff_verify.sh` による全チェック通過（Exit 0）。

## 🛡️ 【必須】開発・実装の制約と前提知識
- 詳細な進行管理および設計議論の実体は [`workspaces/agent_architecture_optimization/`](file:///Users/shoheihasegawa/you_inc/agent-core/workspaces/agent_architecture_optimization/_index.md) を参照せよ。
