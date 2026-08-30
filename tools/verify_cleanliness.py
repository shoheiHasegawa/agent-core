import os
import sys
import json
import argparse
from pathlib import Path

AGENT_CORE_DIR = Path(__file__).resolve().parent.parent

def main():
    parser = argparse.ArgumentParser(description="Verify cleanliness of agent-core")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    results = {
        "status": "success",
        "violations": [],
        "warnings": []
    }

    # 1 & 2. Workspace checks
    workspaces_dir = AGENT_CORE_DIR / "workspaces"
    if workspaces_dir.exists():
        for ws_path in workspaces_dir.iterdir():
            if not ws_path.is_dir():
                continue
            
            ws_name = ws_path.name
            index_path = ws_path / "_index.md"
            progress_path = ws_path / "tasks" / "progress.md"
            context_path = ws_path / "tasks" / "context.md"

            # Check structural integrity
            missing_files = []
            if not index_path.exists(): missing_files.append("_index.md")
            if not progress_path.exists(): missing_files.append("tasks/progress.md")
            if not context_path.exists(): missing_files.append("tasks/context.md")

            if missing_files:
                results["warnings"].append({
                    "type": "legacy_workspace",
                    "workspace": ws_name,
                    "message": f"Missing required files: {', '.join(missing_files)}"
                })

            # Check context.md line count
            if context_path.exists():
                try:
                    lines = context_path.read_text(encoding="utf-8").splitlines()
                    if len(lines) > 50:
                        results["violations"].append({
                            "type": "context_line_limit",
                            "file": str(context_path.relative_to(AGENT_CORE_DIR)),
                            "lines": len(lines),
                            "message": f"context.md exceeds 50 lines (has {len(lines)} lines)"
                        })
                except Exception as e:
                    results["violations"].append({
                        "type": "read_error",
                        "file": str(context_path.relative_to(AGENT_CORE_DIR)),
                        "message": str(e)
                    })

    # 3. Leave No Trace verification (no .tmp or .bak files outside scratch/)
    exclude_dirs = {".venv", ".git", "__pycache__", ".pytest_cache"}
    for root, dirs, files in os.walk(AGENT_CORE_DIR):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".tmp") or file.endswith(".bak"):
                file_path = Path(root) / file
                results["violations"].append({
                    "type": "leave_no_trace",
                    "file": str(file_path.relative_to(AGENT_CORE_DIR)),
                    "message": f"Invalid temporary file found: {file}"
                })

    # 4. Enforce abolition of epics/ directory (Cluster 1 transition)
    epics_dir = AGENT_CORE_DIR / "epics"
    if epics_dir.exists():
        results["violations"].append({
            "type": "legacy_epics_dir",
            "file": "epics/",
            "message": "The epics/ directory is deprecated. Use backlog/ or workspaces/ instead."
        })

    if results["violations"]:
        results["status"] = "failure"

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        if results["status"] == "success":
            print("✅ Cleanliness verification passed.")
            for w in results["warnings"]:
                print(f"⚠️  WARNING: [{w['type']}] Workspace '{w['workspace']}': {w['message']}")
        else:
            print("❌ Cleanliness verification failed!")
            for v in results["violations"]:
                print(f"  - [{v['type']}] {v.get('file', '')}: {v['message']}")
            for w in results["warnings"]:
                print(f"  - WARNING: [{w['type']}] Workspace '{w['workspace']}': {w['message']}")

    if results["status"] == "failure":
        sys.exit(1)

if __name__ == "__main__":
    main()
