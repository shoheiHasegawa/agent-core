#!/usr/bin/env python3
import sys
import traceback
from pathlib import Path

# パス解決
sys.path.append(str(Path(__file__).parent.parent.resolve()))
sys.path.append(str(Path(__file__).parent.parent.parent / "core-service" / "src"))

from app_context import get_core_service_container, SessionLocal

def main():
    print("🔄 Starting Worklog Sync (sync_worklogs)...")
    
    session = SessionLocal()
    try:
        service = get_core_service_container().get_daily_planning_service()
        print("  - Executing DailyPlanningService.sync_worklogs()...")
        service.sync_worklogs()
        session.commit()
        print("✅ Worklog Sync completed successfully.")
    except Exception as e:
        session.rollback()
        error_details = f"Worklog Sync failed: {str(e)}\nTraceback:\n{traceback.format_exc()}"
        print(f"🚨 [FATAL ERROR] {error_details}")
        
        gateway = get_core_service_container().system_event_gateway
        gateway.publish_error("sync_worklogs", error_details)
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    main()
