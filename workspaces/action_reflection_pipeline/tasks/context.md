# Context

## Current State (現在地)
- **Epic 01 〜 Epic 05: タスク管理自動化（Action & Reflection Pipeline）の全工程が完了・本番稼働開始**。
  - **計算エンジン・DDD構造**: `core-service`（9制約スケジューリング、コンテキストアウェア、Super-loose Parser等）がテストカバレッジ90%以上・完全DIで稼働。
  - **夜と朝の自動パイプライン**: `sync_worklogs.py`（実績回収・Leave No Trace）➡ `generate_daily_briefing.py`（18時境界判定/--date対応・Googleカレンダー同期・Obsidian配信）の自動連携。
  - **OSレベル自動化**: `launchd`（`com.youinc.dailypipeline`）による毎晩23:00の自動実行エージェントが常駐化。
  - **対話・トリアージ基盤**: `night-routine`, `inbox-triage`, `priority-planner` 等のスキル群が連動。

## Next Milestones (次のステップ)
- **日常運用**: 毎晩の自動バッチ実行および夜のジャーナリング対話を通じた運用の継続。
- **次のEpic**: `corporate_goal_integration`（会社のABC目標統合）の仕様策定・進行。
