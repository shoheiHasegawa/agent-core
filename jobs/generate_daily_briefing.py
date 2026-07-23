#!/usr/bin/env python3
import sys
import traceback
import subprocess
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

# パス解決

from app_context import get_core_service_container, SessionLocal
def main():
    try:
        print("🌅 Starting Daily Action Planner (generate_daily_briefing)...")
        # JSTで日付を取得
        target_date = datetime.now(ZoneInfo("Asia/Tokyo")).date()
        

        print("  - Injecting dependencies with Unit of Work...")
        session = SessionLocal()
        try:
            service = get_core_service_container().get_daily_planning_service()
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
        gateway = get_core_service_container().get_system_event_gateway()
        gateway.publish_error("generate_daily_briefing", error_details)
        sys.exit(1)

if __name__ == "__main__":
    main()
