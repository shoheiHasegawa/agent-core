#!/usr/bin/env python3
import argparse
import sys
import os
from pathlib import Path

# パス解決
repo_root = Path(__file__).resolve().parent.parent.parent
agent_core_path = repo_root / "agent-core"
core_src_path = repo_root / "core-service" / "src"
sys.path.insert(0, str(agent_core_path))
sys.path.insert(0, str(core_src_path))

from factories.task_management_factory import TaskManagementFactory
from application.task_management.task_management_service import TaskManagementService

def main():
    parser = argparse.ArgumentParser(description="Update/Refine an existing task.")
    parser.add_argument("--task_id", required=True, help="ID of the task to update")
    
    # Priority-Planner 向け引数
    parser.add_argument("--category", help="Task category (e.g., MUST, SHOULD, WANT)")
    parser.add_argument("--estimated_minutes", type=int, help="Estimated minutes")
    parser.add_argument("--status", help="Task status (e.g., TODO, IN_PROGRESS)")

    args = parser.parse_args()

    try:
        task_repo = TaskManagementFactory.create_task_repository()
        task_service = TaskManagementService(task_repo=task_repo)
        
        # refine_task は現状タスクIDを受け取って洗練するロジック
        # 実際には引数として更新項目を渡せるように実装される予定
        kwargs = {}
        if args.category:
            kwargs['category'] = args.category
        if args.estimated_minutes:
            kwargs['estimated_minutes'] = args.estimated_minutes
        if args.status:
            kwargs['status'] = args.status
            
        # 今は refine_task が対応していない可能性があるため、最低限 task_id だけ渡す
        task = task_service.refine_task(task_id=args.task_id, **kwargs)
        
        if task:
            print(f"[SUCCESS] Task updated: {task.id}")
        else:
            print(f"[ERROR] Task not found or update failed: {args.task_id}")
            sys.exit(1)

    except Exception as e:
        print(f"[FATAL] Process failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
