#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

# パス解決
repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(agent_core_path))

from app_context import get_core_service_container, SessionLocal

def backup_queue():
    """Fetch直後に同期的にQueueの状態をGitにコミットして保存する（データ消失防止）"""
    queue_dir = agent_core_path / "queue"
    try:
        # パケットバンドル全体（ディレクトリごと）をAdd
        subprocess.run(["git", "add", str(queue_dir)], check=True, cwd=str(repo_root))
        
        status = subprocess.run(["git", "status", "--porcelain", str(queue_dir)], 
                                capture_output=True, text=True, cwd=str(repo_root))
        if status.stdout.strip():
            subprocess.run(["git", "commit", "-m", "chore(queue): fetch inbox packet bundles and backup"], 
                           check=True, cwd=str(repo_root))
            print("[SUCCESS] Queue backed up to Git.")
        else:
            print("[INFO] No changes to backup.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to backup queue: {e}")

def main():
    try:
        service = MobileVaultFactory.create_service()
        count = service.fetch_to_queue()
        print(f"Total fetched bundles: {count}")
        
        if count > 0:
            backup_queue()
            
    except Exception as e:
        print(f"[FATAL] Fetch failed: {e}")

if __name__ == "__main__":
    main()
