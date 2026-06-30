---
type: epic
status: backlogged
tags: [automation, productivity]
---

# Epic 03: Task and Calendar Automation

## 📖 Background (背景と課題)
タスク管理およびカレンダー連携を手動で行っており、日々の実行コンテキストスイッチやスケジュールの見直しにコストがかかっている。
旧体制からの引き継ぎアイデア（自律型スクレイパー、ローカル音声文字起こし、地政学・AIトレンド収集等）が散在しており、一元化・自動化が求められている。

## 🎯 Goal (目的)
- タスク管理およびカレンダー連携の完全自動化。
- 毎朝のエージェントによる日報サマリー生成・Mobile Vaultへの通知機能 (Dashboard_Briefing) の実現。
- 各種インプット（Web、音声、ニュース等）の自動処理パイプラインの構築。

## 🚧 Scope (やらないこと・境界)
- 現時点では大規模なLLMのファインチューニングなどは行わず、既存のAPIやスクリプトを `core-service` 化して活用する。

## ✅ DoD (完了条件)
- [ ] バックログの整理と設計完了。
- [ ] Dashboard_Briefing 機能の稼働。
- [ ] （オプション）旧体制のアイデア（WhisperやScraper等）の実装・統合。

## 🛡️ 【必須】開発・実装の制約と前提知識 (TO-BE Architecture)
このEpicに紐づく機能開発を行うAgent（Implementer等）は、以下のルールを絶対に遵守せよ。
1. **全体アーキテクチャの把握**: 実装前に必ず `agent-core/docs/architecture/` 配下のシステム構成図とデータフロー図を参照し、全体のデータの流れ（TO-BE）を理解すること。
2. **責務の分離**: ドメインロジック（ビジネスルール）は必ず `core-service` リポジトリ内に実装せよ。APIの呼び出しやバッチの起動などの「運用スクリプト」のみを `agent-core` に配置せよ。
3. **AI防衛網の突破**: `core-service` での実装時は、TDD（テスト駆動）と Feature-Driven Packaging を遵守し、`make check-all` (Linter通過およびカバレッジ90%以上) を必ず達成せよ。
