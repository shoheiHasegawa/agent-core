#!/usr/bin/env python3
import sys
import traceback
from pathlib import Path

# パス解決

from app_context import get_core_service_container, SessionLocal

def main():
    print("🔄 Starting Worklog Sync (sync_worklogs)...")
    
    session = SessionLocal()
    try:
        service = get_core_service_container().get_daily_planning_service()
        print("  - Executing DailyPlanningService.sync_worklogs()...")
        service.sync_worklogs(session)
        session.commit()
        print("✅ Worklog Sync completed successfully.")
    except Exception as e:
        session.rollback()
        print(f"🚨 [FATAL ERROR] Worklog Sync failed: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    main()
