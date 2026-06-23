import os
import sys

# core-serviceへのパスを通す (agent-core/factories から見て ../../core-service/src)
FACTORIES_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_CORE_DIR = os.path.dirname(FACTORIES_DIR)
WORKSPACE_ROOT = os.path.dirname(AGENT_CORE_DIR)
CORE_SERVICE_SRC = os.path.join(WORKSPACE_ROOT, "core-service", "src")
if CORE_SERVICE_SRC not in sys.path:
    sys.path.insert(0, CORE_SERVICE_SRC)

from application.zettelkasten_validator.zettelkasten_service import ZettelkastenService, ZettelkastenConfig
from infrastructure.local_file_repository import LocalFileZettelkastenRepository


def get_zettelkasten_service() -> ZettelkastenService:
    """
    Composition Root for Zettelkasten Service.
    Reads necessary configuration (from agent-core/config or env) and assembles the service with its dependencies.
    """
    # 実際には agent-core/config/ の .env や secret.enc.env をパースして設定を構築する
    conf_path = os.path.join(AGENT_CORE_DIR, "config", "conf.env")
    target_dir = None
    
    if os.path.exists(conf_path):
        with open(conf_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ZETTELKASTEN_PERMANENT_NOTES_DIR="):
                    target_dir = line.split("=", 1)[1]
                    
    if not target_dir:
        raise ValueError("ZETTELKASTEN_PERMANENT_NOTES_DIR is not set in conf.env")
    
    # 1. Config Object を組み立てる (Service-Config Pattern)
    config = ZettelkastenConfig()
    
    # 2. Repository を組み立てる (Data Access Layer)
    repo = LocalFileZettelkastenRepository(target_dir=target_dir)
    
    # 3. Service に依存性を注入して返す (Dependency Injection)
    return ZettelkastenService(config=config, repository=repo)
