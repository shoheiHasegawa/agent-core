#!/usr/bin/env python3
import sys
import os
import argparse

# agent-coreディレクトリへのパスを通す
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_CORE_DIR = os.path.dirname(SCRIPT_DIR)
if AGENT_CORE_DIR not in sys.path:
    sys.path.insert(0, AGENT_CORE_DIR)

# ファクトリをインポート（これにより core-service へのパスも通る）
from factories.zettelkasten import get_zettelkasten_service
from domain.search_query import SearchQuery

def main():
    parser = argparse.ArgumentParser(description="Zettelkasten Search")
    parser.add_argument('--keyword', help="Keyword to search in content")
    parser.add_argument('--tag', help="Tag to search (e.g., #concept/test)")
    parser.add_argument('--alias', help="Alias to search")
    args = parser.parse_args()

    service = get_zettelkasten_service()
    query = SearchQuery(keyword=args.keyword, tag=args.tag, alias=args.alias)

    results = service.search_notes(query)

    print(f"🔍 Found {len(results)} matching notes:")
    for note in results:
        print(f"- {os.path.basename(note.filename)}")

if __name__ == '__main__':
    main()
