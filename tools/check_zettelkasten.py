#!/usr/bin/env python3
import sys
import os

# agent-coreディレクトリへのパスを通す
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
from app_context import get_core_service_container, SessionLocal

def main():
    print(f"🔍 Validating Zettelkasten rules...")

    # ファクトリからServiceを取得（Composition Rootへの依存）
    service = get_core_service_container().get_second_brain_service()

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
