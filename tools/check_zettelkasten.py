#!/usr/bin/env python3
import sys
import os

# agent-coreディレクトリへのパスを通す
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_CORE_DIR = os.path.dirname(SCRIPT_DIR)
if AGENT_CORE_DIR not in sys.path:
    sys.path.insert(0, AGENT_CORE_DIR)

from factories.zettelkasten import get_zettelkasten_service

def main():
    print(f"🔍 Validating Zettelkasten rules...")

    # ファクトリからServiceを取得（Composition Rootへの依存）
    service = get_zettelkasten_service()

    results = service.validate_all_notes()

    if not results:
        print("✅ All Permanent Notes are perfectly valid!")
        sys.exit(0)
    
    print("❌ Zettelkasten Validation Failed!\n")
    for filepath, errors in results.items():
        print(f"File: {filepath}")
        for err in errors:
            print(f"  - {err.message}")
        print()
    
    sys.exit(1)

if __name__ == '__main__':
    main()
