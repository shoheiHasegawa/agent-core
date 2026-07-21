#!/usr/bin/env python3
import sys
import os

# agent-coreディレクトリへのパスを通す
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_CORE_DIR = os.path.dirname(SCRIPT_DIR)
if AGENT_CORE_DIR not in sys.path:
    sys.path.insert(0, AGENT_CORE_DIR)

from factories.second_brain_factory import SecondBrainFactory

def main():
    print(f"🔍 Validating Zettelkasten rules...")

    # ファクトリからServiceを取得（Composition Rootへの依存）
    service = SecondBrainFactory.create_service()

    results = service.audit_zettelkasten_rules()

    if not results:
        print("✅ All Permanent Notes are perfectly valid!")
        sys.exit(0)
    
    print("❌ Zettelkasten Validation Failed!\n")
    for err_msg in results:
        print(f"  - {err_msg}")
    
    sys.exit(1)

if __name__ == '__main__':
    main()
