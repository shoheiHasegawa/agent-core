---
type: epic
status: active
tags: [finance, automation, gas]
---

# Epic: Personal Finance Automation

## 📖 Background (背景と課題)
家計簿、支払い履歴、トレード、資産管理など、個人のお金にまつわる情報の集約・効率化を行う自動化プロジェクト。
旧 `daily-tools-legacy` 等で散発的に作られていたGASスクリプトや財務用モジュールが分散しており、管理・運用コストが高くなっているため、一元管理が必要。

## 🎯 Goal (目的)
- 楽天Pay等の決済履歴の自動収集とZaim等の家計簿ツールへの同期。
- 資産状況の可視化とダッシュボード化。

## 🚧 Scope (やらないこと・境界)
- 複雑な資産運用アルゴリズムの開発はスコープ外（別途 Systematic Trading Architecture などのEpicで扱う）。
- ここでは日々のキャッシュフローと家計簿の自動化に焦点を絞る。

## ✅ DoD (完了条件)
- [ ] 決済履歴の自動収集パイプラインが稼働する。
- [ ] 分散していたGASスクリプトが `agent-core` 管轄下で一元管理または置換される。

## 🛡️ 【必須】開発・実装の制約と前提知識 (TO-BE Architecture)
このEpicに紐づく機能開発を行うAgent（Implementer等）は、以下のルールを絶対に遵守せよ。
1. **全体アーキテクチャの把握**: 実装前に必ず `agent-core/docs/architecture/` 配下のシステム構成図とデータフロー図を参照し、全体のデータの流れ（TO-BE）を理解すること。
2. **責務の分離**: ドメインロジック（ビジネスルール）は必ず `core-service` リポジトリ内に実装せよ。APIの呼び出しやバッチの起動などの「運用スクリプト」のみを `agent-core` に配置せよ。
3. **AI防衛網の突破**: `core-service` での実装時は、TDD（テスト駆動）と Feature-Driven Packaging を遵守し、`make check-all` (Linter通過およびカバレッジ90%以上) を必ず達成せよ。
