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

from application.mobile_vault.config import MobileVaultConfig
from application.mobile_vault.service import MobileVaultService
from infrastructure.mobile_vault.icloud_vault_repository import ICloudVaultRepository

class MobileVaultFactory:
    """
    設定ファイル (conf.env) を読み込み、MobileVaultService を
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
    def create_service(cls) -> MobileVaultService:
        cls.load_config()
        icloud_inbox = os.getenv("ICLOUD_MOBILE_INBOX")
        icloud_attachments = os.getenv("ICLOUD_MOBILE_ATTACHMENTS")
        queue_dir = os.getenv("AGENT_QUEUE_DIR")
        
        if not all([icloud_inbox, icloud_attachments, queue_dir]):
            raise ValueError("Missing environment variables for MobileVaultService in conf.env")
            
        config = MobileVaultConfig(
            icloud_inbox_dir=icloud_inbox,
            icloud_attachments_dir=icloud_attachments,
            agent_queue_dir=queue_dir
        )
        repository = ICloudVaultRepository(
            icloud_inbox_dir=config.icloud_inbox_dir,
            icloud_attachments_dir=config.icloud_attachments_dir
        )
        return MobileVaultService(config=config, repository=repository)

    @classmethod
    def get_task_registry_dir(cls) -> Path:
        cls.load_config()
        path = os.getenv("TASK_REGISTRY_DIR")
        if not path:
            raise ValueError("Missing TASK_REGISTRY_DIR in conf.env")
        return Path(path)
