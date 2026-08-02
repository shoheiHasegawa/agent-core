#!/usr/bin/env python3
import argparse
import json
import os
import select
import sys
from pathlib import Path
from typing import Any, List, Tuple

# パス解決
repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "agent-core"))
sys.path.insert(0, str(repo_root / "core-service" / "src"))

from app_context import get_core_service_container
from application.second_brain.register_inbox_note_dto import RegisterInboxNoteDto
from application.second_brain.register_permanent_note_dto import RegisterPermanentNoteDto
from application.second_brain.register_sense_making_note_dto import RegisterSenseMakingNoteDto


def normalize_tags(raw_tags: Any) -> list[str]:
    if raw_tags is None:
        return []
    if isinstance(raw_tags, list):
        return [str(t).strip() for t in raw_tags if str(t).strip()]
    if isinstance(raw_tags, str):
        return [t.strip() for t in raw_tags.split(",") if t.strip()]
    return []


def parse_input(args: argparse.Namespace) -> list[dict]:
    """
    標準入力 (stdin)、--json 引数、--file 引数、または従来の個別引数からノート情報のリストをパースする。
    """
    # 1. stdin (最優先)
    # isatty() が False かつ stdin に読み取り可能なデータが存在する場合
    if not sys.stdin.isatty():
        rlist, _, _ = select.select([sys.stdin], [], [], 0.0)
        if rlist:
            content = sys.stdin.read().strip()
            if content:
                try:
                    data = json.loads(content)
                    if isinstance(data, dict):
                        return [data]
                    elif isinstance(data, list):
                        return data
                    else:
                        raise ValueError("JSON input must be an object or a list of objects")
                except json.JSONDecodeError:
                    # 後方互換性: --type と --title が指定されている場合はstdinをbodyテキストとして扱う
                    if args.type and args.title:
                        return [_build_legacy_item(args, body_content=content)]
                    raise ValueError("Failed to parse JSON from standard input: invalid JSON format")

    # 2. --json 引数
    if args.json:
        try:
            data = json.loads(args.json)
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                raise ValueError("--json argument must be a JSON object or array")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string in --json: {e}")

    # 3. --file 引数
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            raise FileNotFoundError(f"Specified file does not exist: {file_path}")
        try:
            file_content = file_path.read_text(encoding="utf-8")
            data = json.loads(file_content)
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                raise ValueError("File content must be a JSON object or array")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON content in file {file_path}: {e}")

    # 4. 従来の個別引数 (後方互換)
    if args.type and args.title:
        body_content = ""
        if args.body_file:
            body_path = Path(args.body_file)
            if body_path.exists():
                body_content = body_path.read_text(encoding="utf-8")
            else:
                raise FileNotFoundError(f"body_file not found: {body_path}")
        return [_build_legacy_item(args, body_content=body_content)]

    raise ValueError(
        "No input provided. Provide JSON via stdin, --json, --file, or legacy arguments (--type and --title)."
    )


def _build_legacy_item(args: argparse.Namespace, body_content: str = "") -> dict:
    item = {
        "type": args.type,
        "title": args.title,
        "tags": args.tags or "",
    }
    if args.type == "inbox":
        item["content"] = body_content
    elif args.type == "sense_making":
        item["content"] = body_content
        item["source"] = args.source or ""
    elif args.type == "permanent":
        item["claim"] = args.claim or body_content
        item["context"] = args.context or ""
        item["connections"] = args.connections or ""
    return item


def register_single_note(sb_service: Any, item: dict) -> Tuple[bool, str]:
    if not isinstance(item, dict):
        raise ValueError(f"Expected dict item, got {type(item).__name__}")

    note_type = item.get("type")
    title = item.get("title")

    if not note_type:
        raise ValueError("Missing required field 'type'")
    if not title:
        raise ValueError("Missing required field 'title'")

    tags = normalize_tags(item.get("tags"))

    if note_type == "inbox":
        content = item.get("content") or item.get("body") or ""
        dto = RegisterInboxNoteDto(title=title, content=content, tags=tags)
        saved = sb_service.register_inbox_note(dto)
        return bool(saved), note_type

    elif note_type == "sense_making":
        content = item.get("content") or item.get("body") or ""
        source = item.get("source") or ""
        dto = RegisterSenseMakingNoteDto(title=title, content=content, source=source, tags=tags)
        saved = sb_service.register_sense_making_note(dto)
        return bool(saved), note_type

    elif note_type == "permanent":
        claim = item.get("claim") or item.get("content") or item.get("body") or ""
        context = item.get("context") or ""
        connections = item.get("connections") or ""
        dto = RegisterPermanentNoteDto(
            title=title,
            claim=claim,
            context=context,
            connections=connections,
            tags=tags,
        )
        saved = sb_service.register_permanent_note(dto)
        return bool(saved), note_type

    else:
        raise ValueError(f"Unknown note type: '{note_type}'. Must be one of ['inbox', 'sense_making', 'permanent']")


def main():
    parser = argparse.ArgumentParser(description="Register note(s) into Zettelkasten via core-service.")

    # JSON-First 引数
    parser.add_argument("--json", help="JSON string of a single note object or array of note objects")
    parser.add_argument("--file", help="Path to a JSON file containing note object(s)")

    # 従来の個別引数（後方互換）
    parser.add_argument("--type", choices=["inbox", "sense_making", "permanent"], help="Type of the note to register")
    parser.add_argument("--title", help="Title of the note")
    parser.add_argument("--tags", default="", help="Comma separated tags")
    parser.add_argument("--body_file", help="Path to a file containing the main body content")
    parser.add_argument("--source", default="", help="Source of the note (for sense_making)")
    parser.add_argument("--claim", default="", help="Claim of the note (for permanent)")
    parser.add_argument("--context", default="", help="Context of the note (for permanent)")
    parser.add_argument("--connections", default="", help="Connections of the note (for permanent)")

    args = parser.parse_args()

    try:
        items = parse_input(args)
    except Exception as e:
        error_output = {
            "success": False,
            "registered_count": 0,
            "errors": [str(e)],
        }
        print(json.dumps(error_output, ensure_ascii=False, indent=2))
        sys.exit(1)

    results = []
    errors = []
    registered_count = 0

    try:
        sb_service = get_core_service_container().get_second_brain_service()
    except Exception as e:
        error_output = {
            "success": False,
            "registered_count": 0,
            "errors": [f"Failed to initialize SecondBrainService: {e}"],
        }
        print(json.dumps(error_output, ensure_ascii=False, indent=2))
        sys.exit(1)

    for item in items:
        title = item.get("title", "untitled") if isinstance(item, dict) else "unknown"
        note_type = item.get("type", "unknown") if isinstance(item, dict) else "unknown"
        try:
            saved, verified_type = register_single_note(sb_service, item)
            if saved:
                registered_count += 1
                results.append({
                    "type": verified_type,
                    "title": title,
                    "status": "success",
                })
            else:
                err_msg = f"Failed to save note: {title} (type: {verified_type})"
                errors.append(err_msg)
                results.append({
                    "type": verified_type,
                    "title": title,
                    "status": "failed",
                })
        except Exception as e:
            err_msg = f"Error processing '{title}': {e}"
            errors.append(err_msg)
            results.append({
                "type": note_type,
                "title": title,
                "status": "error",
                "error": str(e),
            })

    success = len(errors) == 0 and registered_count > 0

    output = {
        "success": success,
        "registered_count": registered_count,
    }
    if results:
        output["results"] = results
    if errors:
        output["errors"] = errors

    print(json.dumps(output, ensure_ascii=False, indent=2))
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
