#!/usr/bin/env python3
import sys
import json
from pathlib import Path

# core-service へのパスを通す (agent-core/tools/ -> you_inc/)
current_dir = Path(__file__).parent.resolve()
you_inc_dir = current_dir.parent.parent
core_src_dir = you_inc_dir / "core-service" / "src"
sys.path.insert(0, str(core_src_dir))

from domain.action_pipeline.task import Task, TaskCategory, EnergyLevel, TaskStatus

def validate_task_registry(registry_dir: Path):
    """
    指定されたディレクトリ内のすべてのJSONファイルを読み込み、
    core-service の Task モデルとして正しくパースできるか検証する。
    """
    if not registry_dir.exists():
        print(f"[WARN] Task Registry directory not found at: {registry_dir}")
        print("PASS (No tasks to validate)")
        return

    json_files = list(registry_dir.glob("*.json"))
    if not json_files:
        print("[INFO] No JSON files found in Task Registry.")
        print("PASS")
        return

    errors = []
    for file_path in json_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 必須フィールドのバリデーション
            required_keys = ["id", "title", "category", "energy_level", "estimated_minutes"]
            for key in required_keys:
                if key not in data:
                    errors.append(f"{file_path.name}: Missing required key '{key}'")
            
            # Enum値のバリデーション（インスタンス化テスト）
            if "category" in data:
                TaskCategory(data["category"])
            if "energy_level" in data:
                EnergyLevel(data["energy_level"])
            if "status" in data:
                TaskStatus(data["status"])
                
        except json.JSONDecodeError as e:
            errors.append(f"{file_path.name}: Invalid JSON format - {str(e)}")
        except ValueError as e:
            errors.append(f"{file_path.name}: Invalid Enum value - {str(e)}")
        except Exception as e:
            errors.append(f"{file_path.name}: Unexpected error - {str(e)}")

    if errors:
        print("🚨 [ERROR] Validation Failed!")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✅ [PASS] All Task Registry files are valid.")

if __name__ == "__main__":
    registry_path = current_dir.parent / "data" / "task_registry"
    validate_task_registry(registry_path)
