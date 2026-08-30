#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
# パス解決
repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "agent-core"))
sys.path.insert(0, str(repo_root / "core-service" / "src"))

from app_context import get_core_service_container

def main():
    parser = argparse.ArgumentParser(description="Initialize database schema for core-service.")
    args = parser.parse_args()

    try:
        container = get_core_service_container()
        # SQLAlchemy models must be imported before create_all
        from infrastructure.sqlalchemy.base import Base
        from infrastructure.sqlalchemy.task_model import TaskModel
        from infrastructure.sqlalchemy.worklog_model import WorklogModel
        from infrastructure.sqlalchemy.recurring_task_model import RecurringTaskModel
        from infrastructure.sqlalchemy.agent_task_model import AgentTaskModel
        
        # We need the engine from the container's session
        engine = container.session.get_bind()
        Base.metadata.create_all(bind=engine)
        print("Database schema initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize database: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
