#!/usr/bin/env python3
import sys
import traceback
import subprocess
from pathlib import Path
from datetime import date, datetime

# パス解決 (agent-core/jobs/ -> you_inc/)
current_dir = Path(__file__).parent.resolve()
agent_core_dir = current_dir.parent
core_src_dir = agent_core_dir.parent / "core-service" / "src"
if str(agent_core_dir) not in sys.path:
    sys.path.insert(0, str(agent_core_dir))
if str(core_src_dir) not in sys.path:
    sys.path.insert(0, str(core_src_dir))

from factories.action_pipeline_factory import ActionPipelineFactory
from domain.action_pipeline.task import DailyBriefing

def notify_error(message: str):
    """Macの通知センターにエラーを表示し、エラーログを保存するフェールセーフ機能"""
    print(f"🚨 [FATAL ERROR] {message}")
    
    # エラーログをキューに保存
    error_dir = agent_core_dir / "queue" / "errors"
    error_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    error_file = error_dir / f"scheduler_error_{timestamp}.log"
    
    with open(error_file, "w", encoding="utf-8") as f:
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Error: {message}\n")
        f.write("Traceback:\n")
        f.write(traceback.format_exc())
    
    # Macの通知（AppleScript）を呼び出す
    try:
        subprocess.run([
            "osascript",
            "-e", "on run argv",
            "-e", 'display notification (item 1 of argv) with title "Agent-Core Error" sound name "Basso"',
            "-e", "end run",
            message
        ], check=False)
    except Exception as e:
        print(f"Failed to show Mac notification: {e}")

def main():
    try:
        print("🌅 Starting Daily Scheduler Batch...")
        target_date = date.today()
        
        # 1. 依存性の注入（DI）: ファクトリからリポジトリ等のアダプターを取得
        print("  - Injecting dependencies...")
        task_repo = ActionPipelineFactory.create_task_repository()
        schedule_gateway = ActionPipelineFactory.create_schedule_gateway()
        briefing_repo = ActionPipelineFactory.create_briefing_repository()
        
        # 2. タスク正本から着手可能タスクを取得
        print("  - Reading tasks from Task Registry (SSOT)...")
        tasks = task_repo.get_ready_tasks_for_date(target_date)
        
        if not tasks:
            print("  - No tasks found for today. Generating empty schedule.")
        else:
            print(f"  - Loaded {len(tasks)} tasks.")
            
        # 3. core-service のドメインロジック実行（擬似コード）
        # ※本来は core_service.usecase.daily_planning_service 等を呼び出す
        print("  - Generating schedule blocks (Eat That Frog)...")
        
        # 4. カレンダー同期とBriefing（免罪符）の生成
        print("  - Syncing to Google Calendar...")
        schedule_gateway.sync_schedule(target_date, tasks)
        
        briefing = DailyBriefing(
            target_date=target_date,
            scheduled_tasks=tasks,
            motivation_message="これをやれば今日の勝ちは確定です！👑"
        )
        briefing_repo.save(briefing)
        
        # （タスク状態が変わった場合のみ）Task Registryへ保存し直す
        # task_repo.save_tasks(tasks)
        
        print("✅ Daily Scheduler Batch completed successfully.")
        
    except Exception as e:
        # エラーをキャッチしてフェールセーフ（通知）を発動
        notify_error(f"スケジュール生成バッチが失敗しました: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
