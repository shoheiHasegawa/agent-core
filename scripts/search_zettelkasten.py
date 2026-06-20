#!/usr/bin/env python3
import sys
import os
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
CORE_SERVICE_SRC = os.path.join(WORKSPACE_ROOT, "core-service", "src")
sys.path.insert(0, CORE_SERVICE_SRC)

from core_service.infrastructure.local_file_repository import LocalFileZettelkastenRepository
from core_service.application.zettelkasten_service import ZettelkastenService
from core_service.domain.search_query import SearchQuery

def main():
    parser = argparse.ArgumentParser(description="Zettelkasten Search")
    parser.add_argument('--keyword', help="Keyword to search in content")
    parser.add_argument('--tag', help="Tag to search (e.g., #concept/test)")
    parser.add_argument('--alias', help="Alias to search")
    args = parser.parse_args()

    target_dir = os.path.join(WORKSPACE_ROOT, "second-brain", "40_Permanent_Notes")

    # Dependency Injection
    repo = LocalFileZettelkastenRepository(target_dir=target_dir)
    service = ZettelkastenService(repository=repo)
    query = SearchQuery(keyword=args.keyword, tag=args.tag, alias=args.alias)

    results = service.search_notes(query)

    print(f"🔍 Found {len(results)} matching notes:")
    for note in results:
        print(f"- {os.path.basename(note.filename)}")

if __name__ == '__main__':
    main()
