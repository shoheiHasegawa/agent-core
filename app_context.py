import os
from pathlib import Path
from dotenv import load_dotenv

current_dir = Path(__file__).parent.resolve()
you_inc_dir = current_dir.parent
core_src_dir = you_inc_dir / "core-service" / "src"
agent_core_dir = current_dir

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.sqlalchemy.base import Base

# load config from conf.env and secret.env
load_dotenv(agent_core_dir / "config" / "conf.env")
load_dotenv(agent_core_dir / "config" / "secret.env")

# DB Setup
_db_path = os.environ.get("DB_PATH")
if not _db_path:
    raise ValueError("DB_PATH is not set in config/conf.env")
_engine = create_engine(_db_path, echo=False)
Base.metadata.create_all(_engine)
SessionLocal = sessionmaker(bind=_engine)

from di.config import CoreServiceConfig
from di.container import CoreServiceContainer

def get_core_service_container() -> CoreServiceContainer:
    """
    環境変数から設定を読み込み、Core ServiceのDIコンテナを構築して返す。
    """
    config = CoreServiceConfig(
        db_path=_db_path,
        mobile_inbox_dir=os.environ.get("ICLOUD_MOBILE_INBOX", "/tmp/mobile_inbox"),
        mobile_dashboard_dir=os.environ.get("ICLOUD_MOBILE_DASHBOARD", "/tmp/mobile_dashboard"),
        mobile_attachments_dir=os.environ.get("ICLOUD_MOBILE_ATTACHMENTS", "/tmp/mobile_attachments"),
        agent_queue_dir=os.environ.get("AGENT_QUEUE_DIR", str(agent_core_dir / "queue")),
        google_calendar_id=os.environ.get("TARGET_CALENDAR_ID", "primary"),
        google_credentials_path=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
        
        sb_inbox_dir=os.environ.get("ZETTELKASTEN_INBOX_DIR", "/tmp/sb/inbox"),
        sb_sense_making_dir=os.environ.get("ZETTELKASTEN_SENSE_MAKING_DIR", "/tmp/sb/sense_making"),
        sb_permanent_notes_dir=os.environ.get("ZETTELKASTEN_PERMANENT_DIR", "/tmp/sb/permanent"),
        sb_attachments_dir=os.environ.get("ZETTELKASTEN_ATTACHMENTS_DIR", "/tmp/sb/attachments"),
        sb_inbox_template_path=os.environ.get("ZETTELKASTEN_INBOX_TEMPLATE", ""),
        sb_sense_making_template_path=os.environ.get("ZETTELKASTEN_SENSE_MAKING_TEMPLATE", ""),
        sb_permanent_note_template_path=os.environ.get("ZETTELKASTEN_PERMANENT_TEMPLATE", ""),
        sb_forbidden_patterns=os.environ.get("ZETTELKASTEN_FORBIDDEN_PATTERNS", "90_Meta,attachments").split(",")
    )
    session = SessionLocal()
    return CoreServiceContainer(config, session)
