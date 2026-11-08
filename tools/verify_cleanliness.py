import argparse
import json
import os
import sys
import time
from pathlib import Path

AGENT_CORE_DIR = Path(__file__).resolve().parent.parent


def check_cleanliness(agent_core_dir: Path) -> tuple[list[dict], list[dict]]:
    violations = []
    warnings = []

    # 1 & 2. Workspace checks
    workspaces_dir = agent_core_dir / "workspaces"
    if workspaces_dir.exists():
        for ws_path in workspaces_dir.iterdir():
            if not ws_path.is_dir():
                continue

            ws_name = ws_path.name
            index_path = ws_path / "_index.md"
            agents_path = ws_path / "AGENTS.md"
            context_path = ws_path / "tasks" / "context.md"

            # Check structural integrity (allow either AGENTS.md or legacy _index.md)
            missing_files = []
            if not index_path.exists() and not agents_path.exists():
                missing_files.append("AGENTS.md (or _index.md)")
            if not context_path.exists():
                missing_files.append("tasks/context.md")

            if missing_files:
                warnings.append({
                    "type": "legacy_workspace",
                    "workspace": ws_name,
                    "message": f"Missing required files: {', '.join(missing_files)}",
                })

            # Check stale workspace (updated >= 7 days ago)
            mtimes = []
            for check_file in [agents_path, index_path, context_path]:
                if check_file.exists():
                    mtimes.append(check_file.stat().st_mtime)
            if mtimes:
                latest_mtime = max(mtimes)
                if (time.time() - latest_mtime) >= 7 * 86400:
                    warnings.append({
                        "type": "stale_workspace",
                        "workspace": ws_name,
                        "message": f"Workspace has not been updated for over 7 days (last updated: {time.ctime(latest_mtime)})",
                    })

            # Check context.md line count
            if context_path.exists():
                try:
                    lines = context_path.read_text(encoding="utf-8").splitlines()
                    if len(lines) > 50:
                        violations.append({
                            "type": "context_line_limit",
                            "file": str(context_path.relative_to(agent_core_dir)),
                            "lines": len(lines),
                            "message": f"context.md exceeds 50 lines (has {len(lines)} lines)",
                        })
                except Exception as e:
                    violations.append({
                        "type": "read_error",
                        "file": str(context_path.relative_to(agent_core_dir)),
                        "message": str(e),
                    })

    # 3. Leave No Trace verification (no .tmp or .bak files outside scratch/)
    exclude_dirs = {".venv", ".git", "__pycache__", ".pytest_cache"}
    for root, dirs, files in os.walk(agent_core_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".tmp") or file.endswith(".bak"):
                file_path = Path(root) / file
                violations.append({
                    "type": "leave_no_trace",
                    "file": str(file_path.relative_to(agent_core_dir)),
                    "message": f"Invalid temporary file found: {file}",
                })

    # 4. Enforce abolition of epics/ directory (Cluster 1 transition)
    epics_dir = agent_core_dir / "epics"
    if epics_dir.exists():
        violations.append({
            "type": "legacy_epics_dir",
            "file": "epics/",
            "message": "The epics/ directory is deprecated. Use GitHub Issues and workspaces/ instead.",
        })

    return violations, warnings


def main():
    parser = argparse.ArgumentParser(description="Verify cleanliness of agent-core")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    violations, warnings = check_cleanliness(AGENT_CORE_DIR)

    results = {
        "status": "failure" if violations else "success",
        "violations": violations,
        "warnings": warnings,
    }

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
