#!/usr/bin/env python3
import argparse
import sys
import os
import shutil
import subprocess
from pathlib import Path

# パス解決
repo_root = Path(__file__).resolve().parent.parent.parent
agent_core_path = repo_root / "agent-core"
core_src_path = repo_root / "core-service" / "src"
sys.path.insert(0, str(agent_core_path))
sys.path.insert(0, str(core_src_path))

from factories.mobile_vault_factory import MobileVaultFactory
from factories.second_brain_factory import SecondBrainFactory
from factories.task_management_factory import TaskManagementFactory
from application.task_management.task_management_service import TaskManagementService
from domain.task_management.task import TaskCategory, TaskType

def commit_deletion(packet_dir: Path, msg: str):
    """パケット処理（削除）後にGitに状態をコミットする（対象パケットのみ）"""
    try:
        # パケットディレクトリの削除のみをステージング
        subprocess.run(["git", "add", "--all", str(packet_dir)], check=True, cwd=str(repo_root))
        status = subprocess.run(["git", "status", "--porcelain", str(packet_dir)], capture_output=True, text=True, cwd=str(repo_root))
        if status.stdout.strip():
            subprocess.run(["git", "commit", "-m", msg], check=True, cwd=str(repo_root))
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to commit queue deletion: {e}")
    except FileNotFoundError:
        pass

def main():
    parser = argparse.ArgumentParser(description="Process a packet bundle from Queue.")
    parser.add_argument("--packet_name", required=True, help="Directory name of the packet in Queue (e.g., packet_1234_abc)")
    parser.add_argument("--action", required=True, choices=["task", "idea", "delete"], help="Action to perform")
    
    # Idea 向け引数
    parser.add_argument("--title", help="Title for the idea/task")
    parser.add_argument("--tags", default="", help="Comma separated tags for the idea")
    parser.add_argument("--body_file", help="Path to the file containing formatted body text (to avoid shell escape issues)")
    
    # Task 向け引数
    parser.add_argument("--category", help="Task category (e.g., MUST, SHOULD, WANT)")
    parser.add_argument("--task_type", help="Task type (e.g., ONE_OFF, ROUTINE)")
    parser.add_argument("--estimated_minutes", type=int, help="Estimated minutes")

    args = parser.parse_args()

    # Queue DIR
    MobileVaultFactory.load_config()
    queue_dir_env = os.getenv("AGENT_QUEUE_DIR")
    queue_dir = Path(queue_dir_env).resolve() if queue_dir_env else (agent_core_path / "queue").resolve()
    
    # パストラバーサル脆弱性の防御
    packet_dir = (queue_dir / args.packet_name).resolve()
    if not packet_dir.is_relative_to(queue_dir):
        print(f"[FATAL ERROR] Invalid packet name (Path traversal attempt detected): {args.packet_name}")
        sys.exit(1)

    if not packet_dir.exists() or not packet_dir.is_dir():
        print(f"[ERROR] Packet bundle not found or not a directory: {packet_dir}")
        sys.exit(1)

    try:
        if args.action == "idea":
            sb_service = SecondBrainFactory.create_service()
            title = args.title or args.packet_name
            tags_list = [t.strip() for t in args.tags.split(",") if t.strip()]
            body = ""
            
            if args.body_file:
                body_path = Path(args.body_file)
                if body_path.is_file():
                    try:
                        with open(body_path, "r", encoding="utf-8") as f:
                            body = f.read()
                    except UnicodeDecodeError:
                        print(f"[WARNING] UnicodeDecodeError while reading body_file. Proceeding with empty body.")
            
            saved = sb_service.register_knowledge(title=title, content=body, tags=tags_list)
            print(f"[SUCCESS] Idea structured and saved. Success: {saved}")
            
            shutil.rmtree(packet_dir)
            commit_deletion(packet_dir, f"chore(queue): processed idea and removed bundle {args.packet_name}")

        elif args.action == "task":
            # TaskManagementService 経由で登録
            task_repo = TaskManagementFactory.create_task_repository()
            task_service = TaskManagementService(task_repo=task_repo)
            
            title = args.title or "Untitled Task"
            
            cat_str = args.category or "WANT"
            try:
                category = TaskCategory[cat_str]
            except KeyError:
                category = TaskCategory.WANT
                
            tt_str = args.task_type or "ONE_OFF"
            try:
                task_type = TaskType[tt_str]
            except KeyError:
                task_type = TaskType.ONE_OFF
                
            est_mins = args.estimated_minutes or 30
            
            task = task_service.register_task(
                title=title,
                description="",
                category=category,
                task_type=task_type,
                estimated_minutes=est_mins,
                reference_id=args.packet_name
            )
            
            shutil.rmtree(packet_dir)
            print(f"[SUCCESS] Task registered: {task.id}")
            commit_deletion(packet_dir, f"chore(queue): processed task and removed bundle {args.packet_name}")
            
        elif args.action == "delete":
            shutil.rmtree(packet_dir)
            print(f"[SUCCESS] Packet bundle deleted: {args.packet_name}")
            commit_deletion(packet_dir, f"chore(queue): deleted bundle {args.packet_name}")

    except Exception as e:
        print(f"[FATAL] Process failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
