#!/usr/bin/env python3
import os
import subprocess
import argparse
from pathlib import Path

CURRENT_DIR = Path(__file__).parent.resolve()
AGENT_CORE_DIR = CURRENT_DIR.parent
QUEUE_DIR = AGENT_CORE_DIR / "queue"
YOU_INC_DIR = AGENT_CORE_DIR.parent

def backup_queue():
    """未処理パケットの断面をGitで保存する"""
    print("[INFO] Backing up current queue state...")
    try:
        # git add agent-core/queue/
        subprocess.run(
            ["git", "add", "agent-core/queue/"],
            cwd=YOU_INC_DIR,
            check=True,
            capture_output=True
        )
        
        # 変更があればコミット
        status = subprocess.run(
            ["git", "status", "--porcelain", "agent-core/queue/"],
            cwd=YOU_INC_DIR,
            capture_output=True,
            text=True
        )
        if status.stdout.strip():
            subprocess.run(
                ["git", "commit", "-m", "chore: backup incoming inbox packets"],
                cwd=YOU_INC_DIR,
                check=True,
                capture_output=True
            )
            print("[SUCCESS] Queue backup committed.")
        else:
            print("[INFO] No new packets to backup in queue.")
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to backup queue: {e.stderr.decode('utf-8')}")
        # エラーでも処理は続行する

def read_queue(limit: int = 0):
    """Queueにあるパケットを読み取って出力する"""
    if not QUEUE_DIR.exists():
        print(f"[WARN] Queue directory not found at: {QUEUE_DIR}")
        return

    packets = list(QUEUE_DIR.glob("mobile_packet_*.md"))
    
    if limit > 0:
        packets = packets[:limit]
        
    if not packets:
        print("[INFO] No incoming packets found in queue.")
        return

    print(f"\n=== Found {len(packets)} Packet(s) in Queue ===\n")
    for packet in packets:
        print(f"--- Packet: {packet.name} ---")
        try:
            with open(packet, "r", encoding="utf-8") as f:
                content = f.read()
            print(content)
            print("-" * 40 + "\n")
        except Exception as e:
            print(f"[ERROR] Failed to read {packet.name}: {e}\n")

def main():
    parser = argparse.ArgumentParser(description="Read incoming packets from the inbox queue.")
    parser.add_argument("--limit", type=int, default=0, help="Limit the number of packets to read (0 = no limit)")
    args = parser.parse_args()

    backup_queue()
    read_queue(limit=args.limit)

if __name__ == "__main__":
    main()
