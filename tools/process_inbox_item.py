import sys
import argparse
from pathlib import Path

current_dir = Path(__file__).parent.resolve()
agent_core_dir = current_dir.parent
sys.path.append(str(agent_core_dir))
sys.path.append(str(agent_core_dir.parent / "core-service" / "src"))

from app_context import get_core_service_container

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--item_id", required=True)
    parser.add_argument("--action", choices=["idea", "task", "delete"], required=True)
    parser.add_argument("--title", default="")
    parser.add_argument("--tags", default="") # comma separated
    parser.add_argument("--energy_level", choices=["High", "Low"], default="Low")
    args = parser.parse_args()
    
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

    container = get_core_service_container()
    service = container.get_mobile_vault_service()
    
    success = service.process_inbox_item(
        item_id=args.item_id,
        action=args.action,
        title=args.title,
        tags=tags,
        energy_level=args.energy_level
    )
    if success:
        print(f"Successfully processed {args.item_id} as {args.action}")
    else:
        print(f"Failed to process {args.item_id}")
        sys.exit(1)

if __name__ == "__main__":
    main()
