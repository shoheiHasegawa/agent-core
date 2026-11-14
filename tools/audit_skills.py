#!/usr/bin/env python3
"""
audit_skills.py

agent-core/skills/ 配下の全 SKILL.md およびテンプレートの静的整合性を検証するLinterです。
1. YAML Frontmatter の検証: `name`, `description` が正しく存在すること。
2. 最大行数検証 (Thin Skill 原則): SKILL.md は80行以内であること。
3. 立法と司法の分離（ハードコード防止）: compliance-reviewer が特定個別ルールを直書きしていないか。
4. SSOT整合性検証: 憲法 GEMINI.md のルートと agent-core の同一性検証、正本ドキュメントの WHY 記述検証。
"""

import re
import sys
from pathlib import Path

REQUIRED_FRONTMATTER = ["name", "description"]
MAX_SKILL_LINES = 80


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

    # 2. Line Limit check (Thin Skill principle: <= 80 lines)
    line_count = len(content.splitlines())
    if line_count > MAX_SKILL_LINES:
        errors.append(
            f"{skill_path.parent.name}/SKILL.md: Line count ({line_count}) exceeds limit of {MAX_SKILL_LINES} lines (Thin Skill principle violation)."
        )

    # 3. Hardcoding Check (特定の個別ルール列挙のハードコード検知)
    if skill_path.parent.name == "compliance-reviewer":
        if "Happy Path" in content or "Idempotency" in content:
            errors.append(
                f"{skill_path.parent.name}/SKILL.md: Hardcoded domain rules detected in compliance-reviewer! Must dynamically extract rules from docs/rules/."
            )

    # 4. Dead Link Check (JITロード対象ドキュメント等の実在チェック)
    agent_core_root = Path(__file__).resolve().parent.parent
    linked_paths = set(re.findall(r"agent-core/docs/[\w/.-]+", content))
    for p in linked_paths:
        rel_p = p.removeprefix("agent-core/")
        target_file = agent_core_root / rel_p
        if not target_file.exists():
            errors.append(f"{skill_path.parent.name}/SKILL.md: Dead link detected: '{p}' does not exist.")

    return errors


def find_monorepo_root(agent_core_root: Path) -> Path | None:
    """
    agent-core の配置からモノレポルート（you_inc）を探索する。
    Pass 1: 上位ディレクトリで GEMINI.md が存在し、agent-core/ ディレクトリを持つディレクトリを探索。
    Pass 2: GEMINI.md が欠損している場合でも、兄弟リポ（core-service または second-brain）と agent-core を持つ親ディレクトリを探索。
            ただし worktrees 自体は誤認しないよう除外する。
    モノレポ構造が見つからない場合（単体 checkout 等）は None を返す。
    """
    resolved = agent_core_root.resolve()

    # Pass 1: 正常モノレポ検出（GEMINI.md と agent-core/ が存在）
    for p in resolved.parents:
        if (p / "GEMINI.md").exists() and (p / "agent-core").is_dir():
            return p

    # Pass 2: ルート GEMINI.md 欠損モノレポ検出（兄弟リポと agent-core/ が存在）
    for p in resolved.parents:
        if p.name != "worktrees" and (p / "agent-core").is_dir():
            if (p / "core-service").is_dir() or (p / "second-brain").is_dir():
                return p

    return None


def verify_gemini_identity(agent_core_root: Path, root_gemini_path: Path | None = None) -> list[str]:
    """
    リポジトリ最上位ルートの GEMINI.md と agent-core/GEMINI.md が完全一致することを検証する。
    単体 checkout 環境（root_gemini_path=None かつ find_monorepo_root が None）では比較をスキップする。
    """
    errors = []
    agent_gemini = agent_core_root / "GEMINI.md"

    # agent-core/GEMINI.md 自体の存在・非空チェック
    agent_content = None
    if not agent_gemini.exists():
        errors.append(f"agent-core/GEMINI.md not found at {agent_gemini}")
    else:
        agent_content = agent_gemini.read_text(encoding="utf-8")
        if not agent_content.strip():
            errors.append(f"agent-core/GEMINI.md is empty at {agent_gemini}")

    # root GEMINI.md のパス解決
    target_root_gemini = root_gemini_path
    if target_root_gemini is None:
        monorepo_root = find_monorepo_root(agent_core_root)
        if monorepo_root is not None:
            target_root_gemini = monorepo_root / "GEMINI.md"

    # root GEMINI.md が特定された場合の存在・一致チェック
    if target_root_gemini is not None:
        if not target_root_gemini.exists():
            errors.append(f"Root GEMINI.md not found at {target_root_gemini}")
        elif agent_content and agent_content.strip():
            root_content = target_root_gemini.read_text(encoding="utf-8")
            if root_content != agent_content:
                errors.append(
                    f"GEMINI.md mismatch between root ({target_root_gemini}) and agent-core ({agent_gemini})! "
                    "Global Constitution must be completely identical across both locations."
                )

    return errors


def verify_ssot_docs(agent_core_root: Path) -> list[str]:
    """
    正本ドキュメント（docs/architecture.md, docs/rules/*.md, AGENTS.md, README.md）が:
    1. WHY（存在目的）を明記していること
    2. 移行期の時系列ノイズ（【確定】、ステータス、ロードマップ等）を含まない Timeless SSOT であること
    を機械的に検証する。
    """
    errors = []
    ssot_targets = [
        agent_core_root / "AGENTS.md",
        agent_core_root / "README.md",
        agent_core_root / "docs" / "architecture.md",
    ]
    rules_dir = agent_core_root / "docs" / "rules"
    if rules_dir.exists():
        ssot_targets.extend(sorted(rules_dir.glob("*.md")))

    transient_markers = ["— 【確定】", "—【確定】", "アジャイル実装ロードマップ", "旧19スキル"]

    for doc_path in ssot_targets:
        if not doc_path.exists():
            errors.append(f"SSOT Audit: Required document missing: {doc_path.relative_to(agent_core_root)}")
            continue
        content = doc_path.read_text(encoding="utf-8")
        rel_name = str(doc_path.relative_to(agent_core_root))

        if "WHY" not in content:
            errors.append(
                f"SSOT Audit ({rel_name}): Missing 'WHY' (Document Purpose). Every SSOT document must follow WHY -> WHAT -> HOW."
            )

        for marker in transient_markers:
            if marker in content:
                errors.append(
                    f"SSOT Audit ({rel_name}): Transient/historical marker '{marker}' detected! SSOT documents must be timeless."
                )

    return errors


def main():
    agent_core_root = Path(__file__).resolve().parent.parent
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

    # 2. Audit GEMINI.md Identity
    gemini_errs = verify_gemini_identity(agent_core_root)
    all_errors.extend(gemini_errs)

    # 3. Audit SSOT Documents (WHY -> WHAT -> HOW & Timeless SSOT)
    ssot_errs = verify_ssot_docs(agent_core_root)
    all_errors.extend(ssot_errs)

    if all_errors:
        print("❌ Skill & SSOT Audit Validation Failed!\n")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)

    print(
        f"✅ All {len(skill_files)} SKILL files and SSOT documents mathematically passed WHY-WHAT-HOW and Timeless SSOT audits."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
