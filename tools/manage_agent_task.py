#!/usr/bin/env python3
import argparse
import json
import sys
import select
from pathlib import Path
from typing import Any, Tuple, Optional

# パス解決（agent-core / core-service）
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "agent-core"))
sys.path.insert(0, str(REPO_ROOT / "core-service" / "src"))

from app_context import get_core_service_container

def parse_input(args: argparse.Namespace) -> list[dict]:
    """標準入力、--json引数、またはファイルからJSON入力を受け取ってリストで返す"""
    # 1. stdin (パイプ)
    if not sys.stdin.isatty():
        rlist, _, _ = select.select([sys.stdin], [], [], 0.0)
        if rlist:
            content = sys.stdin.read().strip()
            if content:
                try:
                    data = json.loads(content)
                    return [data] if isinstance(data, dict) else data
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to parse JSON from standard input: {e}")

    # 2. --json
    if args.json:
        try:
            data = json.loads(args.json)
            return [data] if isinstance(data, dict) else data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string in --json: {e}")

    # 3. --file
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            raise FileNotFoundError(f"Specified file does not exist: {file_path}")
        try:
            file_content = file_path.read_text(encoding="utf-8")
            data = json.loads(file_content)
            return [data] if isinstance(data, dict) else data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON content in file {file_path}: {e}")

    raise ValueError("No input provided. Provide JSON via stdin, --json, or --file.")

def handle_action(service: Any, item: dict) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Returns (success, result_dict, error_message)
    """
    action = item.get("action")
    if not action:
        return False, None, "Missing required field 'action'"

    try:
        if action == "add":
            command = item.get("command")
            if not command:
                return False, None, "Action 'add' requires 'command'"
            task_id = service.add_task(command)
            return True, {"action": "add", "task_id": task_id, "status": "PENDING"}, None

        elif action == "checkout":
            worker_id = item.get("worker_id")
            if not worker_id:
                return False, None, "Action 'checkout' requires 'worker_id'"
            
            task = service.checkout_task(worker_id)
            if task is None:
                return True, {"action": "checkout", "task": None, "message": "No pending tasks available"}, None
            else:
                return True, {
                    "action": "checkout",
                    "task": {
                        "id": task.id,
                        "command": task.command,
                        "status": task.status.value,
                        "assigned_to": task.assigned_to,
                        "created_at": task.created_at.isoformat(),
                    }
                }, None

        elif action == "complete":
            task_id = item.get("task_id")
            if not task_id:
                return False, None, "Action 'complete' requires 'task_id'"
            result_data = item.get("result_data")
            service.complete_task(task_id, result_data)
            return True, {"action": "complete", "task_id": task_id, "status": "COMPLETED"}, None

        elif action == "fail":
            task_id = item.get("task_id")
            error_msg = item.get("error_msg")
            if not task_id or not error_msg:
                return False, None, "Action 'fail' requires 'task_id' and 'error_msg'"
            service.fail_task(task_id, error_msg)
            return True, {"action": "fail", "task_id": task_id, "status": "FAILED"}, None

        else:
            return False, None, f"Unknown action: '{action}'"
            
    except Exception as e:
        return False, None, str(e)


def main():
    parser = argparse.ArgumentParser(description="Manage Agent Tasks via core-service.")
    parser.add_argument("--json", help="JSON string of a single task action object or array of objects")
    parser.add_argument("--file", help="Path to a JSON file containing task action object(s)")

    args = parser.parse_args()

    try:
        items = parse_input(args)
    except Exception as e:
        error_output = {
            "success": False,
            "count": 0,
            "errors": [str(e)],
        }
        print(json.dumps(error_output, ensure_ascii=False, indent=2))
        sys.exit(1)

    try:
        service = get_core_service_container().get_agent_task_service()
    except Exception as e:
        error_output = {
            "success": False,
            "count": 0,
            "errors": [f"Failed to initialize AgentTaskService: {e}"],
        }
        print(json.dumps(error_output, ensure_ascii=False, indent=2))
        sys.exit(1)

    results = []
    errors = []
    success_count = 0

    for item in items:
        success, result_data, error_msg = handle_action(service, item)
        if success:
            success_count += 1
            if result_data:
                results.append(result_data)
        else:
            errors.append(error_msg)
            results.append({"action": item.get("action", "unknown"), "status": "error", "error": error_msg})

    is_all_success = len(errors) == 0 and success_count > 0

    output = {
        "success": is_all_success,
        "count": success_count,
        "data": results,
    }
    if errors:
        output["errors"] = errors

    print(json.dumps(output, ensure_ascii=False, indent=2))
    
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
