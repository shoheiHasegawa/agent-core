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
  - ドメインコンテキストを `action_pipeline` から `task_management` にリネームし、Serviceを `DailyActionService` と `TaskManagementService` に再編。
  - **【QA強化】** 空洞化テスト（Empty Assertion）19件の摘発と修正。Tester ➡ QA Reviewer ➡ Implementer の職務分離パイプラインを稼働させ、AIのReward Hacking（テストランナー乗っ取り等）をOrchestratorが撃墜し、最終的にインフラ層の例外系を含む61件すべてのテストをPassさせた。
  - **【負債一掃】** `SqlAlchemy` などの技術名の排除漏れ、および使用されなくなった `json_task_repository` を完全削除し、クリーンなDDD状態を確保。

- `[x]` **Phase 6: コンテキストアウェア・スケジューリング (Workday vs Holiday) の実装**
  - `day_context` (WORKDAY/HOLIDAY/ANY) 概念を導入し、定期タスクの発動可否をコントロール可能に。
  - `holidays` ライブラリの導入と Google Calendar の「終日予定」を統合した Context Resolver を実装。
  - 終日予定を「カレンダー上のブロック（壁）」ではなく、「日のコンテキストを切り替えるメタデータ」として扱うアーキテクチャ方針を決定・明文化（SoR分離の徹底）。

## 🚀 次のアクション (Current Status)
- `[ ]` **Epic 05: 本番移行・試験運用フェーズ (Onboarding & Trial)**
  - `[ ]` **Phase 1: 運用基盤の初期セットアップ**
    - `[x]` Google Calendar API 認証設定 (完了済)
    - `[x]` 対象カレンダーIDの設定確認 (`.env` 等への登録)
    - `[x]` iOSショートカットの実機設定 (完了済)
    - `[ ]` `10_Areas` の見直しと整理（ShouldとWantの属性定義を含む）
    - `[ ]` 生活リズム・パラメータ（起床・就寝・昼食時刻等）の初期設定
    - `[ ]` 朝の自動スケジューリングバッチ (`generate_daily_briefing.py`) の Cron 登録
  - `[ ]` **Phase 1.5: 情報の棚卸しとビジョン・計画の再構築**
    - `[x]` 1. `10_Areas` 配下の見直しと、現在の想い・ビジョンとの擦り合わせ
      - `[x]` アーキテクチャの再定義（4大ドメイン化）
      - `[x]` ジョハリの窓によるプロファイリングと `01_Identity` の再定義
      - `[x]` 既存ルールの再配置と整合性検証（`johari-profiler` SKILL実装完了）
    - `[x]` 2. 以前暫定で洗い出した「ルーティンタスク」の見直しと棚卸し
    - `[x]` 3. 脳内の未完了タスクおよび「埋没タスク（レガシー情報）」の棚卸しと回収
    - `[x]` 4. 生活リズム・パラメータ（起床・就寝・昼食時刻等）の初期設定と明文化
    - `[x]` 5. 今期のABC目標達成のためのスケジュール再計画・タスク化
  - `[ ]` **Phase 2: 初期データの棚卸し（データ移行と仕分け）**
    - `[ ]` 脳内の未完了タスク（初期の種）を Mobile Vault の Inbox に投げ込み、稼働済みの `inbox-triage` (壁打ちフロー) を経由して `Task Registry` に仕分け・登録する。
  - `[ ]` **Phase 3: E2E試験運用 (End-to-End Trial)**
    - `[ ]` 夜間: `sync_worklogs.py` を稼働させ、ダッシュボードの完了実績（バックアップ退避された旧ファイル含む）をパースし、`you_inc_ops.db` のタスクレコードのステータス更新（COMPLETED化）を行えるかを検証する。
    - `[ ]` 夜のジャーナリング: `night-routine` がパケットを検知し、実績サマリをもとにタスク整理のフィードバックループを回せるかを検証する。
    - `[x]` 早朝: バッチ処理をキックし、Googleカレンダーへの自動スケジューリング・予定登録を検証する。（手動連携で成功確認済）
    - `[ ]` 朝の配信: 生成されたタスク一覧（`Briefing.md` 等）が Mobile Vault に確実かつ安全に（既存ファイルを退避して）同期されるか検証する。
