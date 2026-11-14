#!/usr/bin/env python3
"""
check_markdown_links.py

Markdown ファイル内のリンク切れ（壊れたリンク）を静的に検出するLinterです。
- リポジトリ内部リンクの実在性チェック
- モノレポ環境における他リポ横断相対リンクの正規位置実在性チェック
- 単体 checkout 環境における他リポ横断リンクの安全なスキップ
"""

import re
import sys
from pathlib import Path

# 直接実行・パッケージインポート両対応のインポート
try:
    from tools.audit_skills import find_monorepo_root
except ImportError:
    from audit_skills import find_monorepo_root

EXCLUDE_DIRS = {".git", "node_modules", ".venv", "__pycache__", "scratch", ".gemini", "worktrees", "workspaces"}
IGNORE_PREFIXES = (
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
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def check_markdown_links(repo_root: Path) -> list[str]:
    """
    指定されたリポジトリルート配下の Markdown ファイルのリンクを検証し、壊れたリンクのエラー一覧を返す。
    """
    repo_root = repo_root.resolve()
    monorepo_root = find_monorepo_root(repo_root)
    errors = []

    md_files = [
        f for f in repo_root.rglob("*.md")
        if not any(ex in f.relative_to(repo_root).parts for ex in EXCLUDE_DIRS)
    ]

    for md_file in sorted(md_files):
        content = md_file.read_text(encoding="utf-8")
        links = LINK_PATTERN.findall(content)
        rel_md = md_file.relative_to(repo_root)

        for _text, link in links:
            if link.startswith(IGNORE_PREFIXES):
                continue

            clean_link = link.split("#")[0]
            if not clean_link or clean_link.isdigit():
                continue

            if clean_link.startswith("file://"):
                abs_target = Path(clean_link.replace("file://", ""))
                if not abs_target.exists():
                    errors.append(f"Broken link in {rel_md}: {link}")
                continue

            target_path = (md_file.parent / clean_link).resolve()

            if target_path.is_relative_to(repo_root):
                # リポジトリ内部リンク
                if not target_path.exists():
                    errors.append(f"Broken link in {rel_md}: {link}")
            elif monorepo_root is not None:
                # モノレポ環境における外部リポジトリ横断リンク
                canonical_md = monorepo_root / "agent-core" / rel_md
                mono_target = (canonical_md.parent / clean_link).resolve()
                if not mono_target.is_relative_to(monorepo_root) or not mono_target.exists():
                    errors.append(f"Broken link in {rel_md}: {link}")
            # 単体 checkout 環境では外部リポジトリへのリンク検証をスキップ

    return errors


def main():
    repo_root = Path(__file__).resolve().parent.parent
    errors = check_markdown_links(repo_root)

    if errors:
        print("❌ Markdown link check failed!\n")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    print("✅ Markdown link check passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
