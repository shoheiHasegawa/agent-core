---
type: template
status: draft
created: "{{date}}"
updated: "{{date}}"
tags: []
---

# Epic_Charter_Template

## 📖 Background (背景と課題)
（なぜこのEpicを始めるのか、解決したい問題は何か）

## 🎯 Goal (目的)
（このEpicが達成すべき具体的な状態）

## 🚧 Scope (やらないこと・境界)
（スコープクリープを防ぐための制約）

## ✅ DoD (完了条件)
（Agentや人間が「終わった」と判定できる基準）

## 🛡️ 【必須】開発・実装の制約と前提知識 (TO-BE Architecture)
このEpicに紐づく機能開発を行うAgent（Implementer等）は、以下のルールを絶対に遵守せよ。
1. **全体アーキテクチャの把握**: 実装前に必ず `agent-core/docs/architecture/` 配下のシステム構成図とデータフロー図を参照し、全体のデータの流れ（TO-BE）を理解すること。
2. **責務の分離**: ドメインロジック（ビジネスルール）は必ず `core-service` リポジトリ内に実装せよ。APIの呼び出しやバッチの起動などの「運用スクリプト」のみを `agent-core` に配置せよ。
3. **AI防衛網の突破**: `core-service` での実装時は、TDD（テスト駆動）と Feature-Driven Packaging を遵守し、`make check-all` (Linter通過およびカバレッジ90%以上) を必ず達成せよ。
