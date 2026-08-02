#!/bin/bash
set -e

export PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Starting Daily Pipeline ==="
echo "Time: $(date)"
echo "Project Root: $PROJECT_ROOT"

cd "$PROJECT_ROOT"

echo "--- Phase 1: Sync Worklogs ---"
uv run python3 jobs/sync_worklogs.py

echo "--- Phase 2: Generate Daily Briefing ---"
uv run python3 jobs/generate_daily_briefing.py

echo "=== Daily Pipeline Completed Successfully ==="
