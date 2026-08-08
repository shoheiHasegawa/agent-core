#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Paths
AGENT_CORE_DIR = Path(__file__).resolve().parent.parent
TOOLS_DIR = AGENT_CORE_DIR / "tools"
JOBS_DIR = AGENT_CORE_DIR / "jobs"
TEMPLATES_DIR = AGENT_CORE_DIR / "templates"
CONFIG_DIR = AGENT_CORE_DIR / "config"

SKILLS_DIR = AGENT_CORE_DIR / "skills"
DOCS_DIR = AGENT_CORE_DIR / "docs"

def main():
    print("======================================")
    print(" Running Orphan Scripts Audit...")
    print("======================================")

    # Build search corpus for tools/templates
    md_files_to_search = []
    if SKILLS_DIR.exists():
        md_files_to_search.extend(SKILLS_DIR.rglob("*.md"))
    if DOCS_DIR.exists():
        md_files_to_search.extend(DOCS_DIR.rglob("*.md"))
        
    for root_md in ["AGENT.md", "INDEX.md", "README.md", "GEMINI.md"]:
        root_md_path = AGENT_CORE_DIR / root_md
        if root_md_path.exists():
            md_files_to_search.append(root_md_path)
            
    tools_readme = TOOLS_DIR / "README.md"
    if tools_readme.exists():
        md_files_to_search.append(tools_readme)

    reference_text = ""
    for md_file in md_files_to_search:
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                reference_text += f.read() + "\n"
        except Exception:
            pass

    # Build search corpus for launchd/cron (jobs)
    jobs_reference_text = ""
    if CONFIG_DIR.exists():
        for fpath in CONFIG_DIR.rglob("*"):
            if fpath.is_file():
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        jobs_reference_text += f.read() + "\n"
                except Exception:
                    pass

    orphan_found = False

    # 1. Check tools/
    print("=> Checking tools/ ...")
    exclude_tools = {"__init__.py", "audit_orphan_scripts.py"}
    if TOOLS_DIR.exists():
        for tool_file in TOOLS_DIR.glob("*"):
            if tool_file.is_file() and tool_file.suffix in [".py", ".sh"]:
                if tool_file.name in exclude_tools:
                    continue
                if tool_file.name not in reference_text:
                    print(f"  [ORPHAN TOOL] {tool_file.name} is not referenced in any SKILL or docs.")
                    orphan_found = True

    # 2. Check templates/
    print("=> Checking templates/ ...")
    exclude_templates = {".gitkeep"}
    if TEMPLATES_DIR.exists():
        for tmpl_file in TEMPLATES_DIR.glob("*"):
            if tmpl_file.is_file():
                if tmpl_file.name in exclude_templates:
                    continue
                if tmpl_file.name not in reference_text:
                    print(f"  [ORPHAN TEMPLATE] {tmpl_file.name} is not referenced in any SKILL or docs.")
                    orphan_found = True

    # 3. Check jobs/
    print("=> Checking jobs/ ...")
    exclude_jobs = {"__init__.py"}
    if JOBS_DIR.exists():
        for job_file in JOBS_DIR.glob("*"):
            if job_file.is_file() and job_file.suffix in [".py", ".sh"]:
                if job_file.name in exclude_jobs:
                    continue
                # 移行措置として、config/(launchd等) に無ければ、ドキュメント(INDEX.md等) の記載でもパスとする
                if job_file.name not in jobs_reference_text and job_file.name not in reference_text:
                    print(f"  [ORPHAN JOB] {job_file.name} is not referenced in config/ or any docs.")
                    orphan_found = True

    if orphan_found:
        print("\n❌ Orphan files detected! Technical debt found.")
        print("Please remove unused files or add proper references in SKILLs/Docs/Launchd.")
        sys.exit(1)
    else:
        print("\n✅ All tools, templates, and jobs are properly referenced.")
        sys.exit(0)

if __name__ == "__main__":
    main()
