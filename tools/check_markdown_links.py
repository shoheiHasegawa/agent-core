#!/usr/bin/env python3
import re
import sys
from pathlib import Path


def main():
    repo_root = Path(__file__).resolve().parent.parent
    md_files = list(repo_root.rglob("*.md"))
    exclude_dirs = {".git", "node_modules", ".venv", "__pycache__", "scratch", ".gemini", "worktrees", "workspaces"}

    md_files = [f for f in md_files if not any(ex in f.parts for ex in exclude_dirs)]

    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    has_error = False

    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        links = link_pattern.findall(content)
        for _text, link in links:
            if link.startswith(
                (
                    "http",
                    "https",
                    "mailto:",
                    "#",
                    "{{",
                    "kindle:",
                    "obsidian:",
                    "file:///path/to/file",
                    "image.png",
                    "img.png",
                )
            ):
                continue

            clean_link = link.split("#")[0]
            if not clean_link or clean_link.isdigit():
                continue

            if clean_link.startswith("file://"):
                abs_target = Path(clean_link.replace("file://", ""))
                if abs_target.exists():
                    continue
                print(f"❌ Broken link in {md_file.relative_to(repo_root)}: {link}")
                has_error = True
                continue

            target_path = (md_file.parent / clean_link).resolve()
            if not target_path.exists():
                print(f"❌ Broken link in {md_file.relative_to(repo_root)}: {link}")
                has_error = True

    if has_error:
        print("Markdown link check failed!")
        sys.exit(1)
    else:
        print("✅ Markdown link check passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
