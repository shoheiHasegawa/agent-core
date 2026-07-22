import sys
from pathlib import Path
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
# core-service と agent-core のパスを通す
current_dir = Path(__file__).parent.resolve()
you_inc_dir = current_dir.parent.parent
core_src_dir = you_inc_dir / "core-service" / "src"
agent_core_dir = you_inc_dir / "agent-core"

if str(core_src_dir) not in sys.path:
    sys.path.insert(0, str(core_src_dir))
if str(agent_core_dir) not in sys.path:
    sys.path.insert(0, str(agent_core_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.task_management.task_repository import SqlTaskRepository
from infrastructure.task_management.worklog_repository import SQLAlchemyWorklogRepository

# Create SessionLocal bound to you_inc_ops.db
_engine = create_engine(f"sqlite:///{core_src_dir.parent}/you_inc_ops.db", echo=False)
from infrastructure.db.models import Base
Base.metadata.create_all(_engine)
SessionLocal = sessionmaker(bind=_engine)

from domain.task_management.repository import ScheduleGateway, BriefingRepository
from domain.task_management.task import Task, DailyBriefing
from application.task_management.daily_action_service import DailyActionService
from typing import List
from datetime import date

# load config from conf.env and secret.env
load_dotenv(agent_core_dir / "config" / "conf.env")
load_dotenv(agent_core_dir / "config" / "secret.env")

from infrastructure.calendar.config import CalendarConfig
from infrastructure.calendar.google_calendar_repository import GoogleCalendarRepository
from domain.interfaces.calendar_repository import CalendarRepository

from infrastructure.task_management.briefing_repository import MobileVaultBriefingRepository
from infrastructure.mobile_vault.local_file_mobile_vault_repository import LocalFileMobileVaultRepository
import os

class DummyScheduleGateway(ScheduleGateway):
    def sync_schedule(self, target_date: date, tasks: List[Task]) -> None:
        print(f"[DummyGateway] Synced {len(tasks)} tasks to Google Calendar for {target_date}")

class TaskManagementFactory:
    """
    DI（依存性の注入）を組み立てるファクトリクラス。
    core-service のドメインロジックに対し、インフラのアダプターを注入する。
    """
    @staticmethod
    def get_session() -> Session:
        # DBセッションを生成して返す
        return SessionLocal()

    @staticmethod
    def create_task_repository(session: Session = None):
        sess = session or SessionLocal()
        return SqlTaskRepository(sess)
        
    @staticmethod
    def create_worklog_repository(session: Session = None):
        sess = session or SessionLocal()
        return SQLAlchemyWorklogRepository(sess)

    @staticmethod
    def create_schedule_gateway() -> ScheduleGateway:
        # TODO: Google Calendar API 等の連携アダプターを実装し差し替える
        return DummyScheduleGateway()

    @staticmethod
    def create_briefing_repository() -> BriefingRepository:
        inbox_dir = os.environ.get("ICLOUD_MOBILE_INBOX", "/tmp/mobile_inbox")
        mobile_vault_repo = LocalFileMobileVaultRepository()
        return MobileVaultBriefingRepository(mobile_vault_repo, inbox_dir)

    @staticmethod
    def create_calendar_repository() -> CalendarRepository:
        calendar_id = os.environ.get("TARGET_CALENDAR_ID", "primary")
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
        config = CalendarConfig(calendar_id=calendar_id, credentials_path=credentials_path)
        return GoogleCalendarRepository(config)

    @classmethod
    def create_daily_action_service(cls, session: Session) -> DailyActionService:
        """
        トランザクションを共有するためのセッションを受け取り、
        必要なリポジトリを注入した Service を返します。
        """
        task_repo = cls.create_task_repository(session)
        worklog_repo = cls.create_worklog_repository(session)
        schedule_gateway = cls.create_schedule_gateway()
        briefing_repo = cls.create_briefing_repository()
        calendar_repo = cls.create_calendar_repository()
        
        return DailyActionService(
            task_repo=task_repo,
            schedule_gateway=schedule_gateway,
            briefing_repo=briefing_repo,
            worklog_repo=worklog_repo,
            calendar_repo=calendar_repo
        )

    @classmethod
    def create_sync_worklogs_service(cls, session: Session):
        from application.task_management.sync_worklogs_service import SyncWorklogsService
        
        mobile_vault_repo = LocalFileMobileVaultRepository()
        task_repo = cls.create_task_repository(session)
        worklog_repo = cls.create_worklog_repository(session)
        inbox_dir = os.environ.get("ICLOUD_MOBILE_INBOX", "/tmp/mobile_inbox")
        archive_dir = os.environ.get("ICLOUD_MOBILE_ARCHIVE", "/tmp/mobile_archive")
        
        return SyncWorklogsService(
            mobile_vault_repository=mobile_vault_repo,
            task_repository=task_repo,
            worklog_repository=worklog_repo,
            inbox_dir=inbox_dir,
            archive_dir=archive_dir
        )
