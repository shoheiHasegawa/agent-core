#!/bin/bash
set -e

# ==========================================
# Agent-Core Script: Zettelkasten Validator
# ==========================================
# 起動トリガーおよび依存性の注入を行うスクリプト。
# second-brainのパスコンテキストを定義し、core-serviceのステートレスCLIに注入する。

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

TARGET_DIR="$WORKSPACE_ROOT/second-brain/40_Permanent_Notes"
CORE_SERVICE_DIR="$WORKSPACE_ROOT/core-service"

echo "🔍 Validating Zettelkasten rules for: $TARGET_DIR"

export PYTHONPATH="$CORE_SERVICE_DIR/src"
python3 -m application.cli.zettelkasten --dir "$TARGET_DIR"
