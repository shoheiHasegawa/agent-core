# Proj_Action_Reflection_Pipeline Progress Tracker

## 📌 プロジェクト概要
CEO（社長）が管理のプレッシャーから解放され、高いパフォーマンスと精神的なウェルビーイングを両立するための「秘書モデル（Secretary Paradigm）」に基づくスケジューリングのコアエンジンと対話インターフェースを構築する。

## ✅ 完了したEpic
- `[x]` **Epic 01: 構想とアーキテクチャ定義**
  - 秘書モデル、M/S/W分類、リカバリーファースト等のパラダイムを定義済。
- `[x]` **Epic 02: 詳細仕様策定**
  - iOSショートカット連携、カレンダー同期ロジックなどのドキュメント作成。
- `[x]` **Epic 03: core-service (計算エンジン) の実装**
  - 9つのスケジューリング制約を実装し、テスト戦略の改修と専門家レビューを完了。
- `[x]` **Epic 04: 朝夜のジャーナリング/ブリーフィング SKILL の実装**
  - カレンダー同期を「朝の1回」にロックする堅牢なドメインモデルを確立しつつ、日中の予期せぬ洗い替え要求に対してもデータの消失を防ぐ「バックアップ退避（フェイルセーフ）」のアーキテクチャを導入。
  - `night-routine` (Orchestrator), `journaling-counselor` (Worker), `priority-planner` (Worker) の2-Tier SKILL群を実装。
  - プロンプトへのハードコード（立法）を排除し、Orchestratorから引数としてパスやルールを注入（DI）する「JIT Context Loading」を実装。
  - UXを崩壊させる「サブエージェントの伝言ゲーム」を防ぐため、親Agentが自身にルールを読み込ませる「Role Switching (自己状態遷移)」のアーキテクチャモデルを考案し、メタスキル（`skill-architect`, `skill-reviewer`）の原則としてシステムレベルに昇華させた。
  - osascript のシェルインジェクションを修正した安全な `daily_scheduler_batch.py` を実装完了。（※旧JSON運用の `validate_task_registry.py` 等はPhase 5でDB化に伴い刷新済）

- `[x]` **Epic 04-B: システムガバナンスと安全装置の実装**
  - セッション終了時に未検証コードを残さないため、`agent-core/tools/pre_handoff_verify.sh` によるオーケストレーションを実装。
  - `AGENT.md` と `session-manager/SKILL.md` に Commit & Push 義務を明記。
  - `core-service` に `make check-all` を強制する Pre-commit フックを導入。

- `[x]` **Epic 04-C: アーキテクチャの最適化と立法・司法システムの高度化**
  - `inbox-triage` のワークフローをインメモリ（ヒアドキュメント）に統一し、Leave No Trace の思想に準拠。
  - レガシーな `zettelkasten_validator` などを完全にクリーンナップし、`core-service` のカバレッジ 90% 以上、および Linter (Ruff) の警告ゼロを達成。
  - 全テストコードの Docstring にシナリオIDを付与し、アーキテクチャ検証ツール (`validate_sdd.py`) を完全通過。
  - 「事前バックアップでリスクを担保し、実行時はステートレスでシンプルな設計を最優先する」という思想を `GEMINI.md` に **Philosophy** として明文化。
  - `skill-reviewer` および `compliance-reviewer` が、憲法（GEMINI.md）と設計方針（skill_design_principles.md等）の2軸から多角的にレビューを強制するようフォーマットをアップデート。

- `[x]` **Phase 5: JSON廃止とDDD再編および品質保証の徹底**
  - Task RegistryのJSONファイルベースの運用を廃止し、SQLite (`core-service/you_inc_ops.db`) に完全移行。
  - Application層を `daily_planning`, `mobile_vault`, `task_operations` 等に再編し、ステートレスなUseCaseとして各種機能を実装。
  - **【QA強化】** 空洞化テスト（Empty Assertion）19件の摘発と修正。Tester ➡ QA Reviewer ➡ Implementer の職務分離パイプラインを稼働させ、AIのReward Hacking（テストランナー乗っ取り等）をOrchestratorが撃墜し、最終的にインフラ層の例外系を含む61件すべてのテストをPassさせた。
  - **【負債一掃】** `SqlAlchemy` などの技術名の排除漏れ、および使用されなくなった `json_task_repository` を完全削除し、クリーンなDDD状態を確保。

- `[x]` **Phase 6: コンテキストアウェア・スケジューリング (Workday vs Holiday) の実装**
  - `day_context` (WORKDAY/HOLIDAY/ANY) 概念を導入し、定期タスクの発動可否をコントロール可能に。
  - `holidays` ライブラリの導入と Google Calendar の「終日予定」を統合した Context Resolver を実装。
  - 終日予定を「カレンダー上のブロック（壁）」ではなく、「日のコンテキストを切り替えるメタデータ」として扱うアーキテクチャ方針を決定・明文化（SoR分離の徹底）。

- `[x]` **Epic 05: 本番移行・試験運用フェーズ (Onboarding & Trial)** 🏆 COMPLETED
  - `[x]` **Phase 1: 運用基盤の初期セットアップ** (Google Calendar API, launchd常駐化 `com.youinc.dailypipeline` 稼働確認)
  - `[x]` **Phase 1.5: 情報の棚卸しとビジョン・計画の再構築** (4大ドメイン再編, johari-profiler)
  - `[x]` **Phase 2: 初期データの棚卸し（データ移行と仕分け）** (inbox-triage 連携確認)
  - `[x]` **Phase 3: E2E試験運用 (End-to-End Trial)** (実績回収・DB更新・Leave No Trace・自動ブリーフィング配信の実稼働確認)
    - `[x]` Google Calendar API 認証設定 (完了済)
    - `[x]` 対象カレンダーIDの設定確認 (`.env` 等への登録)
    - `[x]` iOSショートカットの実機設定 (完了済)
    - `[x]` `10_Areas` の見直しと整理（ShouldとWantの属性定義を含む）
    - `[x]` 生活リズム・パラメータ（起床・就寝・昼食時刻等）の初期設定
    - `[x]` 回収と生成の自動スケジューリングバッチ (`run_daily_pipeline.sh`) の launchd 登録（ジョブネット化）
  - `[x]` **Phase 1.5: 情報の棚卸しとビジョン・計画の再構築**
    - `[x]` 1. `10_Areas` 配下の見直しと、現在の想い・ビジョンとの擦り合わせ
      - `[x]` アーキテクチャの再定義（4大ドメイン化）
      - `[x]` ジョハリの窓によるプロファイリングと `01_Identity` の再定義
      - `[x]` 既存ルールの再配置と整合性検証（`johari-profiler` SKILL実装完了）
    - `[x]` 2. 以前暫定で洗い出した「ルーティンタスク」の見直しと棚卸し
    - `[x]` 3. 脳内の未完了タスクおよび「埋没タスク（レガシー情報）」の棚卸しと回収
    - `[x]` 4. 生活リズム・パラメータ（起床・就寝・昼食時刻等）の初期設定と明文化
    - `[x]` 5. 今期のABC目標達成のためのスケジュール再計画・タスク化
  - `[x]` **Phase 2: 初期データの棚卸し（データ移行と仕分け）**
    - `[x]` 脳内の未完了タスク（初期の種）を Mobile Vault の Inbox に投げ込み、稼働済みの `inbox-triage` (壁打ちフロー) を経由して `Task Registry` に仕分け・登録する。
  - `[x]` **Phase 3: E2E試験運用 (End-to-End Trial)**
    - `[x]` 夜間: `sync_worklogs.py` を稼働させ、ダッシュボードの完了実績（バックアップ退避された旧ファイル含む）をパースし、`you_inc_ops.db` のタスクレコードのステータス更新（COMPLETED化）を行えるかを検証する。
      - （実績: Super-loose Parser による分数の抽出、メモの引き継ぎ対応、およびFakeモックを用いた完全なDI化・DDD要件準拠のアーキテクチャ改修まで完了）
    - `[x]` 夜のジャーナリング・ワークフロー完遂: 
      - 旧呼称「パケット」を `InboxItem` に統一（ドメインからツールまでコードベース全体をリネーム）
      - ダミーダッシュボードを用いたE2Eテストにて、DBセッション管理の漏れ（DIコンテナ起因）および `worklogs` スキーマ不一致の致命的バグを摘発・修正。
      - 実績回収後、不要になった `Briefing.md` を物理削除する「Leave No Trace」の完全動作を確認。
    - `[x]` 早朝: バッチ処理をキックし、Googleカレンダーへの自動スケジューリング・予定登録を検証する。（手動連携で成功確認済）
    - `[x]` 朝の配信: 生成されたタスク一覧（`Briefing.md` 等）が Mobile Vault に確実かつ安全に同期・クリーンアップ（Sync ➡ 削除 ➡ 新規生成のサイクル）されるか検証する。（完了）

- `[ ]` **Epic 06: 試験運用における不具合修正と同期・持ち越しロジックの改善 (Hardening & Bug Fixes)**
  - 🔍 **根本原因の総括**:
    - **Epic内の設計決定漏れ**:
      1. 「一回限りタスク（One-off）」と「定期ルーティン（Recurring）」のライフサイクル差異（休日の未完了ルーティンを平日に持ち越すべきではないという境界ルール）の未定義。
      2. `03_Calendar_Sync_Logic.md` における `dateTime`（ISO8601開始・終了時刻）の入出力スキーマ定義漏れ。
    - **テストの検証不足（モック過多・観点漏れ）**:
      1. `test_google_calendar_gateway.py` が `mock_build.called` のみを確認し、送信ペイロード（`dateTime` vs `date`）を検証する Contract Test を欠いていた。
      2. `test_auto_assign_tasks_usecase.py` に「定期タスク（Recurring）が未完了だった場合のロールオーバー除外」の複合シナリオテストが抜けていた。

  - `[ ]` **Issue 1: Google Calendar同期の時刻指定化（`dateTime` への移行）**
    - **現象**: カレンダー登録が全て終日（`date`）となり、計算されたタイムブロック（開始・終了時刻）が反映されない。また `end.date` に同日を設定しているためGoogle Calendarの排他仕様により前日にズレて表示される。
    - **原因**: `GoogleCalendarGateway.sync_daily_briefing` で `start: {"date": target_date}`, `end: {"date": target_date}` が固定使用され、`ScheduleBuilder` の計算結果（`task.start_time` / `task.end_time`）が渡されていない。またテストがモック呼び出し有無しか検証していなかった。
    - **対象コード**: `core-service/src/infrastructure/google_api/google_calendar_gateway.py`, `core-service/tests/unit/infrastructure/google_api/test_google_calendar_gateway.py`

  - `[ ]` **Issue 2: 定期タスク（Recurring Tasks）の不適切な翌日持ち越し抑止**
    - **現象**: 休日専用タスク（日曜の「ローテーション家事」等）が未完了だった場合、翌平日（月曜）のダッシュボードに持ち越されてしまう。
    - **原因**: `AutoAssignTasksUseCase` のロールオーバー処理（`get_uncompleted_past_tasks`）において、通常タスクと定期タスクを区別せず、無差別に `target_date` を翌日に更新している。
    - **対象コード**: `core-service/src/application/daily_planning/auto_assign_tasks_usecase.py`, `core-service/src/infrastructure/sqlalchemy/task_repository.py`, `core-service/tests/unit/application/daily_planning/test_auto_assign_tasks_usecase.py`

  - `[ ]` **Issue 3: 過去の同期重複イベントのクリーンアップ**
    - **現象**: 過去のテスト・同期処理の複数回実行により、同一タスクの終日イベントがカレンダー上に重複残留している。
    - **原因**: 同期処理時に該当日（および前後）の既存 `source=you_inc` イベントを適切に洗い替え・クリーンアップするロジックの不足。
    - **対象コード**: `core-service/src/infrastructure/google_api/google_calendar_gateway.py`


