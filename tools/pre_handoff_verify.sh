#!/bin/bash
set -e

AGENT_CORE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "======================================"
echo " Running agent-core Pre-Commit Gate..."
echo "======================================"

cd "$AGENT_CORE_DIR"
make check-all

echo "======================================"
echo "🎉 agent-core verifications passed!"
echo "======================================"
