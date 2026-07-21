#!/usr/bin/env python3
import sys
import traceback
import subprocess
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

# パス解決
current_dir = Path(__file__).parent.resolve()
agent_core_dir = current_dir.parent
core_src_dir = agent_core_dir.parent / "core-service" / "src"
if str(agent_core_dir) not in sys.path:
    sys.path.insert(0, str(agent_core_dir))
if str(core_src_dir) not in sys.path:
    sys.path.insert(0, str(core_src_dir))

from factories.task_management_factory import TaskManagementFactory

def notify_error(message: str):
    """Macの通知センターにエラーを表示し、エラーログを保存する"""
    print(f"🚨 [FATAL ERROR] {message}")
    error_dir = agent_core_dir / "queue" / "errors"
    error_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    error_file = error_dir / f"scheduler_error_{timestamp}.log"
    with open(error_file, "w", encoding="utf-8") as f:
        f.write(f"Timestamp: {timestamp}\nError: {message}\nTraceback:\n{traceback.format_exc()}")
    try:
        subprocess.run(["osascript", "-e", "on run argv", "-e", 'display notification (item 1 of argv) with title "Agent-Core Error" sound name "Basso"', "-e", "end run", message], check=False)
    except:
        pass

def main():
    try:
        print("🌅 Starting Daily Action Planner (generate_daily_briefing)...")
        # JSTで日付を取得
        target_date = datetime.now(ZoneInfo("Asia/Tokyo")).date()
        
        briefing_file = agent_core_dir.parent / f"Briefing_{target_date.strftime('%Y-%m-%d')}.md"
        
        # 上書きロスト防止策
        if briefing_file.exists():
            print(f"⚠️ [WARNING] {briefing_file.name} already exists. Skipping generation to prevent data loss.")
            sys.exit(0)
            
        print("  - Injecting dependencies with Unit of Work...")
        session = TaskManagementFactory.get_session()
        try:
            service = TaskManagementFactory.create_daily_action_service(session)
            print("  - Executing DailyActionService.plan_day()...")
            briefing = service.plan_day(target_date, sync_to_calendar=True)
            session.commit()
            print(f"  - Loaded {len(briefing.scheduled_tasks)} tasks.")
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
        
        # Markdownの生成
        with open(briefing_file, "w", encoding="utf-8") as f:
            f.write(f"# Daily Briefing ({target_date.strftime('%Y-%m-%d')})\n\n")
            
            if briefing.warning_flags:
                f.write("## ⚠️ Warnings\n")
                for w in briefing.warning_flags:
                    f.write(f"- {w.value}\n")
                f.write("\n")
                
            f.write("## Today's Tasks\n")
            for t in briefing.scheduled_tasks:
                # 新しいルーズUXフォーマット
                f.write(f"- [ ] {t.title} (予定: {t.estimated_minutes}m) <!-- id: {t.id} -->\n")
                # 日跨ぎタスクのメモがあれば出力
                if getattr(t, "last_memo", None):
                    f.write(f"  前回メモ: {t.last_memo}\n")
                    
            print(f"  - Generated {briefing_file.name}")
        
        print("✅ Daily Action Planner completed successfully.")
        
    except Exception as e:
        notify_error(f"スケジュール生成が失敗しました: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
