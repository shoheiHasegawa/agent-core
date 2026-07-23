#!/usr/bin/env python3
import argparse
import sys
import os
from pathlib import Path

# パス解決
repo_root = Path(__file__).resolve().parent.parent.parent


from app_context import get_core_service_container, SessionLocal

def main():
    parser = argparse.ArgumentParser(description="Register a note into Zettelkasten via core-service.")
    parser.add_argument("--type", required=True, choices=["inbox", "sense_making", "permanent"], help="Type of the note to register")
    parser.add_argument("--title", required=True, help="Title of the note")
    parser.add_argument("--tags", default="", help="Comma separated tags (must comply with formatting rules)")
    parser.add_argument("--body_file", required=False, default=None, help="Path to a file containing the main body content")
    
    # Specific arguments for Sense Making / Permanent Note
    parser.add_argument("--source", default="", help="Source of the note (for Sense Making)")
    parser.add_argument("--claim", default="", help="Claim of the note (for Permanent Note)")
    parser.add_argument("--context", default="", help="Context of the note (for Permanent Note)")
    parser.add_argument("--connections", default="", help="Connections of the note (for Permanent Note)")

    args = parser.parse_args()

    # 本文の読み込み
    body_content = ""
    if args.body_file:
        body_path = Path(args.body_file)
        if body_path.exists():
            with open(body_path, "r", encoding="utf-8") as f:
                body_content = f.read()
        else:
            print(f"[WARN] body_file not found: {body_path}. Proceeding with empty body.")
    elif not sys.stdin.isatty():
        body_content = sys.stdin.read()

    tags_list = [t.strip() for t in args.tags.split(",") if t.strip()]

    try:
        sb_service = get_core_service_container().get_second_brain_service()
        
        if args.type == "inbox":
            saved = sb_service.register_inbox_note(
                title=args.title,
                content=body_content,
                tags=tags_list
            )
        elif args.type == "sense_making":
            saved = sb_service.register_sense_making_note(
                title=args.title,
                content=body_content,
                source=args.source,
                tags=tags_list
            )
        elif args.type == "permanent":
            saved = sb_service.register_permanent_note(
                title=args.title,
                claim=args.claim or body_content, # fallback if body_file used instead of claim
                context=args.context,
                connections=args.connections,
                tags=tags_list
            )
        else:
            raise ValueError(f"Unknown type: {args.type}")

        if saved:
            print(f"[SUCCESS] Registered {args.type} note: {args.title}")
        else:
            print(f"[ERROR] Failed to register {args.type} note.")
            sys.exit(1)

    except Exception as e:
        print(f"[FATAL] Registration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
