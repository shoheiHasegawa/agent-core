#!/usr/bin/env python3
"""
audit_skills.py

agent-core/skills/ 配下の全 SKILL.md およびテンプレートの静的整合性を検証するLinterです。
1. YAML Frontmatter の検証: `name`, `description` が正しく存在すること。
2. グローバル・スキーマ検証: 実行手順内に Action（アクション）タグが含まれていること。
3. 立法と司法の分離（ハードコード防止）: compliance-reviewer が特定個別ルールを直書きしていないか。
4. SSOT整合性検証: spec_template.md と core-service testing_strategy.md の6大観点定義の一致。
"""

import re
import sys
from pathlib import Path

REQUIRED_FRONTMATTER = ["name", "description"]


def audit_skill_file(skill_path: Path) -> list[str]:
    errors = []
    content = skill_path.read_text(encoding="utf-8")

    # 1. Frontmatter check
    if not content.startswith("---"):
        errors.append(f"{skill_path.parent.name}/SKILL.md: Frontmatter delimiter '---' missing at start.")
    else:
        parts = content.split("---", 2)
        if len(parts) < 3:
            errors.append(f"{skill_path.parent.name}/SKILL.md: Frontmatter improperly closed.")
        else:
            fm_text = parts[1]
            for req in REQUIRED_FRONTMATTER:
                if not re.search(rf"^{req}\s*:", fm_text, re.MULTILINE):
                    errors.append(f"{skill_path.parent.name}/SKILL.md: Missing required frontmatter field '{req}'.")

    # 2. Schema Check: Action タグが含まれているか
    if "実行手順" in content or "Steps" in content or "Workflow" in content:
        if not re.search(r"\*(?:\s+|\s*\*\*)[Aa]ction(?:\s*\(Action\))?\*\*", content) and not re.search(
            r"\*(?:\s+|\s*\*\*)[Aa]ction\*\*", content
        ) and not re.search(r"アクション", content):
            errors.append(
                f"{skill_path.parent.name}/SKILL.md: Execution steps missing standard 'Action / アクション' tag."
            )

    # 3. Hardcoding Check (特定の個別ルール列挙のハードコード検知)
    if skill_path.parent.name == "compliance-reviewer":
        if "Happy Path" in content or "Idempotency" in content:
            errors.append(
                f"{skill_path.parent.name}/SKILL.md: Hardcoded domain rules detected in compliance-reviewer! Must dynamically extract rules from docs/rules/."
            )

    # 4. Dead Link Check (JITロード対象ドキュメント等の実在チェック)
    # skill_path: <repo_root>/agent-core/skills/<skill_name>/SKILL.md
    repo_root = skill_path.parent.parent.parent.parent
    linked_paths = set(re.findall(r"agent-core/docs/[\w/.-]+", content))
    for p in linked_paths:
        target_file = repo_root / p
        if not target_file.exists():
            errors.append(f"{skill_path.parent.name}/SKILL.md: Dead link detected: '{p}' does not exist.")

    return errors


def verify_template_ssot(repo_root: Path) -> list[str]:
    """spec_template.md と testing_strategy.md の6大観点が同期しているかを検証"""
    errors = []
    spec_template = repo_root / "agent-core" / "templates" / "spec_template.md"
    testing_strategy = repo_root / "core-service" / "docs" / "rules" / "testing_strategy.md"

    if not spec_template.exists():
        errors.append(f"Missing spec_template.md at {spec_template}")
        return errors
    if not testing_strategy.exists():
        errors.append(f"Missing testing_strategy.md at {testing_strategy}")
        return errors

    template_content = spec_template.read_text(encoding="utf-8")
    strategy_content = testing_strategy.read_text(encoding="utf-8")

    dimensions = [
        "Happy Path",
        "Idempotency",
        "Boundary",
        "Reconciliation",
        "Fault Tolerance",
        "Domain Invariants",
    ]

    for dim in dimensions:
        if dim not in template_content:
            errors.append(f"spec_template.md is missing dimension '{dim}'")
        if dim not in strategy_content:
            errors.append(f"testing_strategy.md is missing dimension '{dim}'")

    return errors


def main():
    agent_core_root = Path(__file__).parent.parent
    repo_root = agent_core_root.parent
    skills_dir = agent_core_root / "skills"

    if not skills_dir.exists():
        print(f"❌ Skills directory not found at {skills_dir}")
        sys.exit(1)

    all_errors = []

    # 1. Audit Skills
    skill_files = list(skills_dir.rglob("SKILL.md"))
    if not skill_files:
        print("❌ No SKILL.md files found.")
        sys.exit(1)

    for skill_file in sorted(skill_files):
        errs = audit_skill_file(skill_file)
        all_errors.extend(errs)

    # 2. Audit SSOT Template Sync
    template_errs = verify_template_ssot(repo_root)
    all_errors.extend(template_errs)

    if all_errors:
        print("❌ Skill & SSOT Audit Validation Failed!\n")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)

    print(f"✅ All {len(skill_files)} SKILL files and SSOT templates mathematically passed architecture and format audits.")
    sys.exit(0)


if __name__ == "__main__":
    main()
