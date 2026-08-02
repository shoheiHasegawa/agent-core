# Jobs (日次・バッチ運用 Runbook)

本ディレクトリは、You_Inc システムにおける日次パイプラインおよび定期実行バッチジョブの正本スクリプト群です。

---

## スクリプト一覧と責務

| スクリプト | 責務 | 呼び出し元 / トリガー |
| :--- | :--- | :--- |
| [`run_daily_pipeline.sh`](./run_daily_pipeline.sh) | 日次パイプラインの統合実行シェル（Phase 1: 実績回収 ➡ Phase 2: 計画生成） | 夜の対話完了時、または早朝の自動/手動実行 |
| [`sync_worklogs.py`](./sync_worklogs.py) | Mobile Vault上の `Briefing_YYYY-MM-DD.md` をスキャンし、実績UPSERT & 単発タスク完了更新 & 物理ファイル自動削除（Leave No Trace） | `run_daily_pipeline.sh` (Phase 1) |
| [`generate_daily_briefing.py`](./generate_daily_briefing.py) | スケジューリング（9大制約）、Google Calendarへの一方向Sync（Reconciliation）、および `Briefing_YYYY-MM-DD.md` の配信 | `run_daily_pipeline.sh` (Phase 2) |

---

## 実行仕様と動的解決ロジック

### 1. 18:00 境界ルール (Target Date Dynamic Resolution)
`generate_daily_briefing.py` は、引数なしで実行された場合に現在のシステム時刻から対象日（`target_date`）を自律判定します。

* **18:00 〜 23:59 の実行**: 「明日」の計画（`tomorrow`）を生成します（夜のジャーナリング終了後の翌日準備）。
* **00:00 〜 17:59 の実行**: 「今日」の計画（`today`）を生成します（早朝の起動や日中のリスケジュール）。
* **明示的な日付指定**: `--date YYYY-MM-DD`（または `-d`）を渡すことで、任意の日付のブリーフィングを強制再生成・同期できます。

```bash
# 動的判定による日次パイプライン実行
./jobs/run_daily_pipeline.sh

# 特定の日付を指定して計画を再生成
uv run python3 jobs/generate_daily_briefing.py --date 2026-08-03
```

---

## 運用手順と障害リカバリー (Operational Procedures)

### 1. 通常運用フロー
1. **夜の振り返り終了時**: `night-routine` スキルの対話完了後、Agentまたはユーザーが `./jobs/run_daily_pipeline.sh` を実行。前日分の実績回収と翌日のブリーフィング配信・カレンダー配置が一括で完了します。
2. **早朝起動時**: 前夜にパイプラインを実行しなかった場合、朝に `./jobs/run_daily_pipeline.sh` を実行すれば、未回収実績の回収と当日のブリーフィング配信が自動で行われます。

### 2. 障害時のリカバリー手順（ステートレス運用原則）
* **誤完了（誤って `[x]` を付けたまま同期してしまった場合）**:
  * システム的な「Undo（復元）機能」は提供しません。投下時間はDBに正しく計上されているため、ユーザーまたはAgentは**「〇〇（残り）」という新規タスクをDBに登録**し直して次回パイプラインへ回します。
* **Google Calendar との不整合が発生した場合**:
  * カレンダー上のイベントを手動で個別削除・修正する必要はありません。`generate_daily_briefing.py --date YYYY-MM-DD` を再実行すれば、Reconciliationロジックによりカレンダー側が自動的にDB正本の状態へ完全洗い替え（INSERT/UPDATE/DELETE）されます。
* **ジョブ実行エラー時**:
  * エラー発生時は `SystemEventGateway` により `agent-core/queue/error_*.md` が自動投函され、次回のAgentセッションで自律的なトリアージ・修復対象となります。
