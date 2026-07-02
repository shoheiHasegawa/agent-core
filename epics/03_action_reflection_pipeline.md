---
type: epic
status: backlogged
tags: [automation, productivity, journaling]
---

# Epic 03: Action & Reflection Pipeline (行動と内省の自動化)

## 📖 Background (背景と課題)
日々のタスク管理やカレンダー設定にかかる認知コスト（計画疲れ）をなくし、「実行（Action）」にのみ集中できる環境が必要である。
また、行動をやりっ放しにせず、摩擦のないジャーナリングを通して自己との対話を行い、システムのインプット（Reflection）とするフィードバックループの構築が求められている。

## 🎯 Goal (目的)
- 「今日何をするか」を考える認知コストをゼロにする（カレンダーとタスクの自動連携）。
- 摩擦のない「振り返り（ジャーナリング）」のループを構築する。
- **【重要】** 単なるタスク処理に陥らないよう、北極星となる「今どこへ向かっているのか（Focus/Direction）」を `10_Areas` などの直下に定義し、毎日のジャーナリング・行動が常にその目標と紐づく状態を作る。

## 🚧 Scope (境界)
**【In Scope（実現すること）】**
- **「どこへ向かうか」のコンパス（目標・フォーカス）の定義と `10_Areas` への配置**
- Timeblocking（タスクのカレンダー自動割り当て）の仕組み構築
- Dashboard Briefing（朝のアクションプラン提示）機能
- Journaling System（スマホや音声等から摩擦なく入力でき、Agentが整理する仕組み）

**【Out of Scope（やらないこと）】**
- 情報収集（地政学・AIトレンド等のWebスクレイピング収集等）は対象外。
- 重厚な四半期・年間目標管理システム（複雑なOKRツール等）のフルスクラッチ開発。

## ✅ DoD & Task Backlog (タスク一覧)
システム全体のアーキテクチャが固まったため、ここからは以下のフェーズに沿って設計・実装を進めます。

### Phase 1: 詳細設計（仕様の策定）👈 完了 🎉
- [x] **`02_Formatter_Logic.md` の作成**: サテライト（`Drop_Zone`）に投げ込まれた「汚いメモ」を、Agentがどういうルールでパースし、`second-brain` 用の綺麗なタスクやナレッジに変換するか（プロンプトや正規表現のルール）を定義する。
- [x] **`03_Calendar_Sync_Logic.md` の作成**: `second-brain` にあるタスクやYAMLのルーティン予定を、Google Calendar APIにどう流し込むか（カレンダーへの登録条件、色分け、重複制御など）を定義する。
- [x] **`04_Journaling_Prompt.md` の作成**: 朝のブリーフィングの出力フォーマット（Briefing.md）と、夜の対話でAgentが投げる「問い」の具体的な内容を定義する。

### Phase 2: 実装・環境構築
- [ ] **サテライト環境の構築**: iCloud Drive上に `Satellite_Vault` フォルダ（01_Drop_Zone, 02_Briefing, 03_Reference等）を作成する。
- [x] **iOSショートカットの作成**: iPhoneから `00_Inbox` に摩擦ゼロでメモを保存するためのショートカット（アクションボタン用メニュー）のレシピを設計・提供する。
- [ ] **`core-service` 実装**: Google Calendar APIクライアントの構築と、Markdownタスクパーサーの実装（TDDで実行）。
- [ ] **`agent-core` 実装**: 朝晩に `core-service` を叩くバッチ処理（cron/launchd）と、夜の対話用スキル（`journaling-coach`等）を実装する。

### Phase 3: 魂の注入と本稼働
- [ ] **コンパスの設定**: `10_Areas`（例えば `01_Executive/` 等）に、今どこへ向かうのか（Focus）を定義したルール/目標ファイルを策定する。
- [ ] 本番環境でのエンドツーエンドテストを実施し、日々の運用ループを回し始める。本Epicをクローズする。

## 🛡️ 制約と前提知識 (TO-BE Architecture)
1. ドメインロジックは `core-service` に、運用バッチは `agent-core` に配置すること。
2. Whisper等の音声入力インターフェースを活用する場合は、入力の「摩擦を極限まで減らす」ことを最優先に設計すること。
