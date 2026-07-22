#!/usr/bin/env python3
import sys
import traceback
from pathlib import Path

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
    print("🔄 Starting Worklog Sync (sync_worklogs)...")
    
    session = TaskManagementFactory.get_session()
    try:
        service = TaskManagementFactory.create_sync_worklogs_service(session)
        print("  - Executing SyncWorklogsService.sync()...")
        service.sync()
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
