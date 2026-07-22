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
def main():
    try:
        print("🌅 Starting Daily Action Planner (generate_daily_briefing)...")
        # JSTで日付を取得
        target_date = datetime.now(ZoneInfo("Asia/Tokyo")).date()
        

        print("  - Injecting dependencies with Unit of Work...")
        session = TaskManagementFactory.get_session()
        try:
            service = TaskManagementFactory.create_daily_action_service(session)
            print("  - Executing DailyActionService.plan_day()...")
            briefing = service.plan_day(target_date, sync_to_calendar=True)
            session.commit()

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

        print("  - Saved daily briefing to Mobile Vault via BriefingGateway.")
        print("✅ Daily Action Planner completed successfully.")
        
    except Exception as e:
        error_details = f"スケジュール生成が失敗しました: {str(e)}\nTraceback:\n{traceback.format_exc()}"
        gateway = TaskManagementFactory.create_system_event_gateway()
        gateway.publish_error("generate_daily_briefing", error_details)
        sys.exit(1)

if __name__ == "__main__":
    main()
