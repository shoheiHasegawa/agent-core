import sys
from pathlib import Path

# core-service と agent-core のパスを通す
current_dir = Path(__file__).parent.resolve()
you_inc_dir = current_dir.parent.parent
core_src_dir = you_inc_dir / "core-service" / "src"
agent_core_dir = you_inc_dir / "agent-core"

if str(core_src_dir) not in sys.path:
    sys.path.insert(0, str(core_src_dir))
if str(agent_core_dir) not in sys.path:
    sys.path.insert(0, str(agent_core_dir))

from infrastructure.json_task_repository import JsonTaskRepository
# モック用のダミーGateway（本来は外部API連携）
from domain.action_pipeline.repository import IScheduleGateway, IBriefingRepository
from domain.action_pipeline.task import Task, DailyBriefing
from typing import List
from datetime import date

class DummyScheduleGateway(IScheduleGateway):
    def sync_schedule(self, target_date: date, tasks: List[Task]) -> None:
        print(f"[DummyGateway] Synced {len(tasks)} tasks to Google Calendar for {target_date}")

class DummyBriefingRepository(IBriefingRepository):
    def save(self, briefing: DailyBriefing) -> None:
        print(f"[DummyBriefing] Saved briefing for {briefing.target_date}")

class ActionPipelineFactory:
    """
    DI（依存性の注入）を組み立てるファクトリクラス。
    core-service のドメインロジックに対し、agent-core のアダプターを注入する。
    """
    @staticmethod
    def create_task_repository() -> JsonTaskRepository:
        registry_path = current_dir.parent / "data" / "task_registry"
        return JsonTaskRepository(registry_path)

    @staticmethod
    def create_schedule_gateway() -> IScheduleGateway:
        # TODO: Google Calendar API 等の連携アダプターを実装し差し替える
        return DummyScheduleGateway()

    @staticmethod
    def create_briefing_repository() -> IBriefingRepository:
        # TODO: iCloud(Satellite Vault) へのMarkdown出力アダプターを実装し差し替える
        return DummyBriefingRepository()
