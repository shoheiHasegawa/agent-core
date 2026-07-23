#!/usr/bin/env python3
import sys
import os
import argparse

# agent-coreディレクトリへのパスを通す
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ファクトリをインポート（これにより core-service へのパスも通る）
from app_context import get_core_service_container, SessionLocal

def main():
    parser = argparse.ArgumentParser(description="Zettelkasten Search")
    parser.add_argument('--keyword', help="Keyword to search in content")
    parser.add_argument('--tag', help="Tag to search (e.g., #concept/test)")
    parser.add_argument('--alias', help="Alias to search")
    args = parser.parse_args()

    service = get_core_service_container().get_second_brain_service()
    
    # In SecondBrainService, search takes a string. We use keyword if provided.
    query_str = args.keyword or args.tag or args.alias or ""

    results = service.search_notes(query_str)

    print(f"🔍 Found {len(results)} matching notes:")
    for note in results:
        print(f"- {note}")

if __name__ == '__main__':
    main()
