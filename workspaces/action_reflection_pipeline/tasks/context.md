# Context

## Current State (現在地)
- **Phase 4: TDDによる実装フェーズ** (Epic 03~05相当の再構築) が完了。
- DB(SQLite)への定期タスク移行、および `day_context` (WORKDAY/HOLIDAY/ANY) を用いた**Context Aware Scheduling**（祝日・有給の自動判定と動的スケジューリング）の実装が完了した。
- 終日予定を「メタデータ・フラグ」として扱うアーキテクチャ方針を決定し、各種ドキュメント(`spec.md`, `00_Design_Decisions_and_Paradigms.md`)への明文化も完了。
- テストおよび `validate_sdd.py` によるアーキテクチャ検証は全て Pass している。

## Current Focus (次回の論点・着手領域)
- **Google Calendar (外部SoR) との実際の連携実装**
  - 現在モックやスタブ状態となっている `GoogleCalendarRepository` の実装を進め、決定したスケジュール(`DailyBriefing`)を対象のカレンダーに同期(Export)する処理の実装。
  - OAuthやサービスアカウント等の認証機構の整備。
  - 同期済みイベントの差分更新や冪等性の担保（Google Calendar API側のEvent ID等を利用）。エンドツーエンドの挙動確認
  - `night-routine` による振り返りフィードバックサイクルの検証
  - Macの `cron` や `launchd` による完全自動化（ハンズフリー化）のセットアップ
