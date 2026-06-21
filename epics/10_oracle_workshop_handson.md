---
type: epic
status: active
tags: [infrastructure, oracle, aws]
---

# Epic 10: Oracle Workshop Hands-on Environment

## 📖 Background (背景と課題)
7月頭までに改修してサブ講師として利用する予定のアクティブなプロジェクト。
旧 `daily-tools-legacy/oracle-workshop` からそのままディレクトリごと昇格・移動してきた。
ハンズオン用の環境準備を手動で行うとコストと手間がかかるため、自動化が必要。

## 🎯 Goal (目的)
- ハンズオン環境（Windows AMI、EC2インスタンス）の迅速な展開と破棄。
- 勉強会終了後の確実なリソース削除によるコスト最適化。

## 🚧 Scope (やらないこと・境界)
- 現状のCloudFormationやスクリプトベースの展開ロジックの抜本的な書き換え（Terraform化など）は当面行わない。既存資産を活かす。

## ✅ DoD (完了条件)
- [ ] 7月の勉強会用の環境が1コマンドで立ち上がる状態にする。
- [ ] 終了後に確実にリソースをクリーニングできる仕組みを確認する。

## 🛡️ 【必須】開発・実装の制約と前提知識 (TO-BE Architecture)
このEpicに紐づく機能開発を行うAgent（Implementer等）は、以下のルールを絶対に遵守せよ。
1. **全体アーキテクチャの把握**: 実装前に必ず `agent-core/docs/architecture/` 配下のシステム構成図とデータフロー図を参照し、全体のデータの流れ（TO-BE）を理解すること。
2. **責務の分離**: ドメインロジック（ビジネスルール）は必ず `core-service` リポジトリ内に実装せよ。APIの呼び出しやバッチの起動などの「運用スクリプト」のみを `agent-core` に配置せよ。
3. **AI防衛網の突破**: `core-service` での実装時は、TDD（テスト駆動）と Feature-Driven Packaging を遵守し、`make check-all` (Linter通過およびカバレッジ90%以上) を必ず達成せよ。
