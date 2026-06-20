#!/usr/bin/env python3
import sys
import os

# core-serviceへのパスを通す
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
CORE_SERVICE_SRC = os.path.join(WORKSPACE_ROOT, "core-service", "src")
sys.path.insert(0, CORE_SERVICE_SRC)

from core_service.infrastructure.local_file_repository import LocalFileZettelkastenRepository
from core_service.application.zettelkasten_service import ZettelkastenService

def main():
    target_dir = os.path.join(WORKSPACE_ROOT, "second-brain", "40_Permanent_Notes")
    print(f"🔍 Validating Zettelkasten rules for: {target_dir}")

    # Dependency Injection
    repo = LocalFileZettelkastenRepository(target_dir=target_dir)
    service = ZettelkastenService(repository=repo)

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
