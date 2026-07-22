import os
import re
import sys
import traceback
import subprocess
from pathlib import Path
from datetime import datetime

# パス解決
current_dir = Path(__file__).parent.resolve()
agent_core_dir = current_dir.parent
core_src_dir = agent_core_dir.parent / "core-service" / "src"

if str(agent_core_dir) not in sys.path:
    sys.path.insert(0, str(agent_core_dir))
if str(core_src_dir) not in sys.path:
    sys.path.insert(0, str(core_src_dir))

from factories.task_management_factory import TaskManagementFactory
from factories.system_event_factory import SystemEventFactory
from domain.task_management.task import Worklog



class SyncWorklogsTool:
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.agent_core_dir = self.workspace_root / "agent-core"
        self.queue_dir = self.agent_core_dir / "queue"

    def run(self, briefing_path: str):
        filepath = Path(briefing_path)
        if not filepath.is_file():
            raise FileNotFoundError(f"Briefing file not found or is not a file: {filepath}")

        filename = filepath.name
        date_match = re.search(r'Briefing_(\d{4}-\d{2}-\d{2})\.md', filename)
        if not date_match:
            raise ValueError(f"Invalid briefing filename: {filename}")
        
        worked_date_str = date_match.group(1)
        worked_date = datetime.strptime(worked_date_str, "%Y-%m-%d").date()

        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        worklogs = []
        
        # ステートマシン用変数
        current_task_id = None
        current_is_checked = False
        current_estimated = 0
        current_actual = None
        current_memo_lines = []
        is_in_memo = False

        def finish_current_task():
            nonlocal current_task_id, current_is_checked, current_estimated, current_actual, current_memo_lines
            if current_task_id:
                final_minutes = 0
                if current_actual is not None:
                    final_minutes = current_actual
                elif current_is_checked:
                    final_minutes = current_estimated
                
                final_memo = "\n".join(current_memo_lines).strip() if current_memo_lines else None
                
                if final_minutes > 0 or current_is_checked or final_memo:
                    worklogs.append(Worklog(
                        task_id=current_task_id,
                        minutes=final_minutes,
                        is_completed=current_is_checked,
                        memo=final_memo
                    ))
            
            # Reset state
            current_task_id = None
            current_is_checked = False
            current_estimated = 0
            current_actual = None
            current_memo_lines = []
            is_in_memo = False

        # ブロック・パーサー
        for line in lines:
            line_str = line.strip()
            
            # 新しいタスク行の開始検知: - [x] タスクA (予定: 30m) 45 <!-- id: task123 -->
            task_match = re.search(r'^- \[(x|X| )\] .*?\(予定:\s*(\d+)m?\)(.*?)(?:<!--\s*id:\s*([\w\-]+)\s*-->)', line_str)
            if task_match:
                finish_current_task() # 前のタスクを確定
                
                current_is_checked = task_match.group(1).lower() == 'x'
                current_estimated = int(task_match.group(2))
                suffix_text = task_match.group(3).strip()
                current_task_id = task_match.group(4)
                
                # 行末の数字（実績の上書き）をチェック
                if suffix_text and suffix_text.isdigit():
                    current_actual = int(suffix_text)
                    
                is_in_memo = False
                continue
                
            # タスクブロック内での処理
            if current_task_id:
                if line_str.startswith("実績:"):
                    val = line_str.replace("実績:", "").strip()
                    if val.isdigit():
                        current_actual = int(val)
                    is_in_memo = False
                elif line_str.startswith("メモ:"):
                    memo_val = line_str.replace("メモ:", "", 1).strip()
                    if memo_val:
                        current_memo_lines.append(memo_val)
                    is_in_memo = True
                elif is_in_memo and line_str and not line_str.startswith("- [") and not line_str.startswith("前回メモ:"):
                    # メモの続き（インデントされているか、空行でないか）
                    current_memo_lines.append(line_str)
        
        # 最後のタスクを確定
        finish_current_task()

        if not worklogs:
            print("No worklogs found in the briefing.")
            return

        # App Service経由での統合保存（トランザクション保護）
        session = TaskManagementFactory.get_session()
        try:
            service = TaskManagementFactory.create_daily_action_service(session)
            service.record_worklogs(worked_date, worklogs)
            session.commit()
            print(f"Successfully processed {len(worklogs)} tasks via DailyActionService.")
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

        # サマリー生成
        self.queue_dir.mkdir(exist_ok=True)
        summary_path = self.queue_dir / "event_harvest_achievements.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"# Harvest Achievements Summary ({worked_date_str})\n\n")
            for wl in worklogs:
                status = "COMPLETED" if wl.is_completed else "IN PROGRESS"
                memo_str = f" [Memo: {wl.memo}]" if wl.memo else ""
                f.write(f"- Task {wl.task_id}: {wl.minutes} min [{status}]{memo_str}\n")

if __name__ == "__main__":
    import sys
    workspace = str(Path(__file__).parent.parent.parent.resolve())
    agent_core_dir = Path(workspace) / "agent-core"
    
    if len(sys.argv) > 1:
        briefing_path = sys.argv[1]
        tool = SyncWorklogsTool(workspace)
        try:
            tool.run(briefing_path)
            print("Done.")
        except Exception as e:
            error_details = f"Worklog Sync Failed: {str(e)}\nTraceback:\n{traceback.format_exc()}"
            gateway = SystemEventFactory.create_gateway()
            gateway.publish_error("sync_worklogs", error_details)
            sys.exit(1)
    else:
        print("Usage: sync_worklogs.py <path_to_briefing_md>")
