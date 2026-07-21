import os
import sys
from pathlib import Path

# core-service へのパスを通す
FACTORIES_DIR = Path(__file__).resolve().parent
AGENT_CORE_DIR = FACTORIES_DIR.parent
WORKSPACE_ROOT = AGENT_CORE_DIR.parent
CORE_SERVICE_SRC = WORKSPACE_ROOT / "core-service" / "src"

if str(CORE_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SERVICE_SRC))

from application.second_brain.config import SecondBrainConfig
from application.second_brain.service import SecondBrainService
from infrastructure.second_brain.local_file_second_brain_repository import LocalFileSecondBrainRepository

class SecondBrainFactory:
    """
    設定ファイル (conf.env) を読み込み、SecondBrainService を
    組み立てて提供する Composition Root (工場)。
    """
    @staticmethod
    def load_config():
        conf_path = AGENT_CORE_DIR / "config" / "conf.env"
        if conf_path.exists():
            with open(conf_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        os.environ[key.strip()] = val.strip()

    @classmethod
    def create_service(cls) -> SecondBrainService:
        cls.load_config()
        # Set absolute base path for the repository
        sb_base = Path(os.getenv("SB_BASE_DIR", str(WORKSPACE_ROOT / "second-brain")))
        
        inbox_dir = os.getenv("SB_INBOX_DIR", "00_Inbox")
        sense_making_dir = os.getenv("SB_SENSE_MAKING_DIR", "20_Sense_Making")
        permanent_notes_dir = os.getenv("SB_PERMANENT_NOTES_DIR", "40_Permanent_Notes")
        attachments_dir = os.getenv("SB_ATTACHMENTS_DIR", "90_Meta/Attachments")
        
        inbox_template = os.getenv("SB_INBOX_TEMPLATE_PATH", "90_Meta/Templates/Inbox_Raw_Template.md")
        sense_making_template = os.getenv("SB_SENSE_MAKING_TEMPLATE_PATH", "90_Meta/Templates/Sense_Making_Template.md")
        permanent_template = os.getenv("SB_PERMANENT_NOTE_TEMPLATE_PATH", "90_Meta/Templates/Permanent_Note.md")
        
        config = SecondBrainConfig(
            inbox_dir=inbox_dir,
            sense_making_dir=sense_making_dir,
            permanent_notes_dir=permanent_notes_dir,
            attachments_dir=attachments_dir,
            inbox_template_path=inbox_template,
            sense_making_template_path=sense_making_template,
            permanent_note_template_path=permanent_template,
            forbidden_patterns=["10_Areas", "10_Projects"]
        )
        
        repository = LocalFileSecondBrainRepository(base_path=str(sb_base))
        
        return SecondBrainService(config=config, repository=repository)
