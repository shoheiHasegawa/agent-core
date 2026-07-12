#!/usr/bin/env python3
import argparse
import sys
import os
import shutil
import json
import datetime
import uuid
import subprocess
from pathlib import Path

# パス解決
repo_root = Path(__file__).resolve().parent.parent.parent
agent_core_path = repo_root / "agent-core"
sys.path.append(str(agent_core_path))

from factories.mobile_vault_factory import MobileVaultFactory
from factories.second_brain_factory import SecondBrainFactory

def commit_deletion(queue_dir: Path, msg: str):
    """パケット処理（削除）後にGitに状態をコミットする"""
    try:
        subprocess.run(["git", "add", "-A", str(queue_dir)], check=True, cwd=str(repo_root))
        status = subprocess.run(["git", "status", "--porcelain", str(queue_dir)], capture_output=True, text=True, cwd=str(repo_root))
        if status.stdout.strip():
            subprocess.run(["git", "commit", "-m", msg], check=True, cwd=str(repo_root))
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to commit queue deletion: {e}")

def main():
    parser = argparse.ArgumentParser(description="Process a packet bundle from Queue.")
    parser.add_argument("--packet_name", required=True, help="Directory name of the packet in Queue (e.g., packet_1234_abc)")
    parser.add_argument("--action", required=True, choices=["task", "idea", "delete"], help="Action to perform")
    
    # Idea 向け引数
    parser.add_argument("--title", help="Title for the idea/task")
    parser.add_argument("--tags", default="", help="Comma separated tags for the idea")
    parser.add_argument("--body_file", help="Path to the file containing formatted body text (to avoid shell escape issues)")
    
    # Task 向け引数
    parser.add_argument("--category", help="Task category (e.g., M, S, I)")
    parser.add_argument("--energy_level", help="Task energy level (e.g., High, Medium, Low)")
    parser.add_argument("--estimated_minutes", type=int, help="Estimated minutes")

    args = parser.parse_args()

    # Queue DIR を環境変数 (Factoryのロード経由) またはデフォルトパスから取得
    MobileVaultFactory.load_config()
    queue_dir_env = os.getenv("AGENT_QUEUE_DIR")
    queue_dir = Path(queue_dir_env) if queue_dir_env else agent_core_path / "queue"
    
    packet_dir = queue_dir / args.packet_name

    if not packet_dir.exists() or not packet_dir.is_dir():
        print(f"[ERROR] Packet bundle not found: {packet_dir}")
        sys.exit(1)

    try:
        if args.action == "idea":
            # core-service の Parser (ドメインロジック) を呼び出し
            sb_service = SecondBrainFactory.create_service()
            
            title = args.title or args.packet_name
            tags_list = [t.strip() for t in args.tags.split(",") if t.strip()]
            
            # body_file から本文を読み取る
            body = ""
            if args.body_file:
                body_path = Path(args.body_file)
                if body_path.exists():
                    with open(body_path, "r", encoding="utf-8") as f:
                        body = f.read()
                else:
                    print(f"[WARN] body_file not found: {body_path}. Proceeding with empty body.")
            
            # SecondBrainService による保存
            saved = sb_service.register_knowledge(title=title, content=body, tags=tags_list)
            print(f"[SUCCESS] Idea structured and saved. Success: {saved}")
            
            # オーケストレーション層の責務としてパケット削除とコミットを実行
            shutil.rmtree(packet_dir)
            commit_deletion(queue_dir, f"chore(queue): processed idea and removed bundle {args.packet_name}")

        elif args.action == "task":
            # Task Registry への登録
            task_id = str(uuid.uuid4())
            task_data = {
                "id": task_id,
                "title": args.title or "Untitled Task",
                "category": args.category or "I",
                "energy_level": args.energy_level or "Medium",
                "estimated_minutes": args.estimated_minutes or 30,
                "status": "TODO",
                "created_at": datetime.datetime.now().isoformat()
            }
            task_registry_dir = MobileVaultFactory.get_task_registry_dir()
            task_registry_dir.mkdir(parents=True, exist_ok=True)
            task_file = task_registry_dir / f"{task_id}.json"
            
            with open(task_file, "w", encoding="utf-8") as f:
                json.dump(task_data, f, ensure_ascii=False, indent=2)
            
            shutil.rmtree(packet_dir)
            print(f"[SUCCESS] Task registered: {task_id}")
            commit_deletion(queue_dir, f"chore(queue): processed task and removed bundle {args.packet_name}")
            
        elif args.action == "delete":
            shutil.rmtree(packet_dir)
            print(f"[SUCCESS] Packet bundle deleted: {args.packet_name}")
            commit_deletion(queue_dir, f"chore(queue): deleted bundle {args.packet_name}")

    except Exception as e:
        print(f"[FATAL] Process failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
