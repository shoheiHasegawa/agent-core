import sys
from pathlib import Path

current_dir = Path(__file__).parent.resolve()
agent_core_dir = current_dir.parent
sys.path.append(str(agent_core_dir))
sys.path.append(str(agent_core_dir.parent / "core-service" / "src"))

import json
from app_context import get_core_service_container

def main():
    container = get_core_service_container()
    service = container.get_mobile_vault_service()
    inbox_items = service.peek_inbox()
    print(json.dumps(inbox_items, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
