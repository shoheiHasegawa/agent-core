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

# (将来的に) second-brain や agent-core の検証もここに追加可能

echo "======================================"
echo "🎉 All verifications passed! Ready to commit."
echo "======================================"
