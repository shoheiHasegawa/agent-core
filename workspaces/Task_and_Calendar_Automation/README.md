# スマホUIとTask/Calendar自動化プロジェクト (Mobile UI & Task Architecture)

## 🎯 プロジェクトの目的と背景 (Why)
「日常の行動優先順位が定まらず、フォーカスできていない」という課題を根本的に解決する。
人間の役割を「週末のCEO（計画）」と「平日のWorker（実行）」に完全分離し、システム側のAI（PMエージェント）が両者を橋渡しする。
iPhoneのネイティブUI（カレンダー・リマインダー・ウィジェット）を「最強の実行UI」としてハックし、平日は「スマホの指示に従うだけで完璧な一日が終わる」状態を作り出す。

---

## 🏛️ アーキテクチャ設計とUXポリシー (How)

プロジェクトの肥大化を防ぎ、決定の背景（ラショナール）を明確にするため、詳細な設計・アーキテクチャおよびモバイルUXの運用フローについては、以下のドキュメント（インラインADR）に分割して管理する。

*   **[01_System_Architecture.md](01_Design/01_System_Architecture.md)**
    *   データHub（Google Calendar）の役割、PM Agentの実行トリガー（launchdによる夜間バッチ）、iOS入力の正規化方針などのシステム全体アーキテクチャ図と決定事項。
*   **[02_Mobile_UX_and_Daily_Flow.md](01_Design/02_Mobile_UX_and_Daily_Flow.md)**
    *   iPhoneのホーム画面構成案、ディープリンクを活用したUX連携、およびユーザーとシステムの1日の運用フロー（朝・昼・夜のシナリオ）。

---

## 📅 現在の優先順位 (Roadmap: 2026-06-08)

1. **Phase 8**: PM Agent (LLM) による Triage と iOS連携 (Current Focus)
2. **Phase 7**: [x] Nightly Job-Net パイプライン基盤の構築 (Completed)
3. **Tech Debt**: [x] アーキテクチャ技術的負債の解消 & Linter導入 (Completed)
4. **Phase 3**: 自動ロギングとCoachエージェントの導入

---

## 🚀 完了の定義 (DoD: Definition of Done)

### Phase 1: プレゼンテーション層の統合とAPI環境構築
- [x] アプリ専用Googleアカウント（`hs.app1ifeaut0@gmail.com`）のCalendar API有効化およびローカル疎通検証の成功（2026-05-30）。
- [x] ユーザー様のライフサイクルに基づいた「帰社日（旧BOLDAY）」「勉強会（サブ講師）」を含む定例予定（`Routines.md`）の設計・配置完了。
  - *進捗*: 在宅（月金）・出社（火〜木・帰社日金曜）それぞれのフォーカス時間や週末リセット（家事）のタスクプール制をYAMLを含めて完全構築。
- [x] 平文の `credentials.json` や `token.json` の安全な `.gitignore` 防御と、`credentials.enc.json` の SOPS 暗号化コミット完了。

### Phase 2: 入力層とPMエージェント（自動スケジューリング）の構築
- [ ] iOSリマインダー（またはショートカット）からInboxにプレーンテキストを投げ込める。
- [x] PMエージェントがInboxを解析し、Googleカレンダーに自動でタイムブロック（予定枠）を登録できる。
  - [x] COOモジュールの `domain/` (Task, TaskPool, DailySchedule等) のTDD実装完了（Data/Policy vs Mechanismの分離）
  - [x] `life-automation` 側の `application` 層 (`DailyPlanningService` ファサード) および `infrastructure` 層 (Google Calendar同期Fake, Mobile Vault出力) のTDD実装完了

### Phase 6: Life Portfolio Architecture Revamp & COO Integration
- [x] Life Portfolio概念 (Work/Growth/Maintenance/Play/Buffer) の導入と `DailySchedule` への統合。
- [x] 祝日自動除外 (`HolidayDetectionService`) および Buffer自動生成 (`BufferGenerationPolicy`) の実装。
- [x] Sub-Agent Review Board による SOLID/DDD アーキテクチャの完全分離 (Domain Service, Factory の導入)。
  - *Detail*: Application Service（`DailyPlanningService`）が直接ローカルファイルを操作せず、引数で `TaskPool` を受け取り・返す設計とし、副作用のコミット権限を呼び出し元へ移譲。
  - *Detail*: `MobileVaultAdapter` によるインフラの詳細隠蔽、アトミックなファイル書き込み（`os.replace`）、およびインフラ例外のドメイン例外（`MobileVaultSyncError`等）への翻訳。
  - *Detail*: Google Calendar API 通信における `tenacity` を用いた指数的バックオフのリトライ機構と、`dry_run` モードのサポートによる耐障害性の向上。

### Tech Debt (System Defrag & Clean Up)
- [x] アーキテクチャの技術的負債解消とLinter開発 (2026-06-08)
  - *Detail*: 不要なインフラ層「〇〇er」の一掃、ディレクトリ構造のクリーンアップ。
  - *Detail*: `second-brain` 側の `verify_knowledge.py` による自動Linterの導入。

### Phase 7: Nightly Job-Net パイプラインの構築 (Completed)
- [x] 旧アーキテクチャ（分散したplist等）の完全クリーンアップ。
- [x] SQLiteベースの AgentQueue（ジョブキュー）を廃止し、よりシンプルで堅牢な「Nightly Batch」直列パイプラインへピボット（ADR 11）。
- [x] `launchd` によるデーモン（ワーカープロセス）の常駐化（`com.antigravity.nightly_batch.plist`）。
- [x] モバイルからの回収（`mobile_vault`）とスケジューリング（`daily_planning`）の統合。

### Phase 8: PM Agent (LLM) による Triage と iOS連携 (Current Focus)
- [ ] 夜間バッチ内で軽量モデル（Gemini 1.5 Flash等）を用いた `00_Drop_Zone` のルーティング・タスク抽出機能の実装。
- [ ] iOSのショートカットからInboxにプレーンテキスト（1思考1ファイル、日時付き）を投げ込める仕組みの構築。
- [ ] Oura Ring等のデータと、カレンダーの実績データが自動でデイリーノートに記録される。
  - *Detail*: `life-automation` 側に `collect_actuals`（カレンダーの実際の実績枠の取得）および `reallocate_tasks`（未完了タスクのTaskPoolへのリスケジュール戻し）の機能を実装する。
- [ ] Coachエージェントとの週末の振り返り用プロンプト/システムが稼働する。
