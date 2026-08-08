#!/bin/bash
set -e

# ルートディレクトリを取得 (you_inc)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "======================================"
echo " Running Pre-Handoff Verification..."
echo "======================================"

# core-service の検証
echo "=> Verifying core-service..."
cd "$ROOT_DIR/core-service"
make check-all
echo "✅ core-service verified successfully."

# agent-core の検証 (スキル監査・SDD検証・孤立ツールの監査等)
echo "=> Verifying agent-core (Quality Gates)..."
cd "$ROOT_DIR/agent-core"
uv run python tools/verify_cleanliness.py
make check-all
echo "✅ agent-core verified successfully."
echo "======================================"
echo "🎉 All verifications passed! Ready to commit."
echo "======================================"
