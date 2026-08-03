#!/usr/bin/env python3
import argparse
from datetime import date
from pathlib import Path
import sys

# パス解決
repo_root = Path(__file__).resolve().parent.parent.parent
agent_core_path = repo_root / "agent-core"

from app_context import get_core_service_container
from domain.task_management.task import TaskCategory, TaskStatus, TaskType


def main():
    parser = argparse.ArgumentParser(description="Update/Refine an existing task.")
    parser.add_argument("--task_id", required=True, help="ID of the task to update")
    parser.add_argument("--title", help="New title for the task")
    parser.add_argument("--category", help="Task category (MUST, SHOULD, WANT)")
    parser.add_argument("--estimated_minutes", type=int, help="Estimated minutes (> 0)")
    parser.add_argument("--status", help="Task status (TODO, IN_PROGRESS, COMPLETED, INCOMPLETE)")
    parser.add_argument("--deadline", help="Deadline date (YYYY-MM-DD)")
    parser.add_argument("--target_date", help="Target date (YYYY-MM-DD)")
    parser.add_argument("--memo", help="Memo or progress notes")
    parser.add_argument("--task_type", help="Task type (ONE_OFF, ROUTINE, RECURRING)")
    parser.add_argument("--area_id", help="Area ID (e.g. 01_Work, 02_Health)")
    parser.add_argument("--energy_level", help="Energy level (High, Normal, Low)")

    args = parser.parse_args()

    try:
        task_service = get_core_service_container().get_task_operations_service()

        kwargs = {}
        if args.title is not None:
            kwargs["title"] = args.title

        if args.category is not None:
            kwargs["category"] = TaskCategory[args.category.upper()]

        if args.estimated_minutes is not None:
            kwargs["estimated_minutes"] = args.estimated_minutes

        if args.status is not None:
            kwargs["status"] = TaskStatus[args.status.upper()]

        if args.deadline is not None:
            kwargs["deadline"] = date.fromisoformat(args.deadline)

        if args.target_date is not None:
            kwargs["target_date"] = date.fromisoformat(args.target_date)

        if args.memo is not None:
            kwargs["last_memo"] = args.memo

        if args.task_type is not None:
            kwargs["task_type"] = TaskType[args.task_type.upper()]

        if args.area_id is not None:
            kwargs["area_id"] = args.area_id

        if args.energy_level is not None:
            kwargs["energy_level"] = args.energy_level

        task = task_service.refine_task(task_id=args.task_id, **kwargs)

        print(f"[SUCCESS] Task updated: {task.id} (Title: '{task.title}', Status: {task.status.value})")

    except ValueError as e:
        print(f"[ERROR] Validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[FATAL] Process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
