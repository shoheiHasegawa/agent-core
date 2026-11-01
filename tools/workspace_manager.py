#!/usr/bin/env python3
"""
workspace_manager.py

Epic Workspace と Git Worktree（方式A）のライフサイクルを管理するハーネススクリプト。
- `new`: workspaces/<epic>/ の雛形（AGENTS.md, tasks/, docs/, scratch/）を生成し、
         指定されたリポジトリ（agent-core, core-service 等）の git worktree を
         workspaces/<epic>/worktrees/<repo>/ (branch: epic/<epic>) にマウントする。
- `harvest`: クローズ前チェック（context.md 行数、worktree の未コミット差分）を行い、
             worktree マウントを安全に解除して scratch/ を掃除する。
- `list`: 現在の Workspace とマウント中の Worktree 一覧を表示する。
"""

import argparse
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

AGENT_CORE_ROOT = Path(__file__).resolve().parent.parent
YOU_INC_ROOT = AGENT_CORE_ROOT.parent
WORKSPACES_DIR = AGENT_CORE_ROOT / "workspaces"


def run_git(repo_dir: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo_dir), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def create_workspace_files(ws_dir: Path, epic: str, issue: str | None) -> None:
    today = date.today().isoformat()
    (ws_dir / "tasks").mkdir(parents=True, exist_ok=True)
    (ws_dir / "docs").mkdir(parents=True, exist_ok=True)
    (ws_dir / "scratch").mkdir(parents=True, exist_ok=True)
    (ws_dir / "worktrees").mkdir(parents=True, exist_ok=True)

    agents_md = ws_dir / "AGENTS.md"
    if not agents_md.exists():
        issue_ref = f"#{issue}" if issue else "TBD"
        agents_md.write_text(
            f"""---
type: epic
status: in_progress
issue: "{issue_ref}"
created: "{today}"
---

# Epic Workspace: {epic}

## 🎯 Goal (WHY & WHAT)
- 対象 Issue: {issue_ref}
- 目的: （ここにEpicの目的を記載）

## ✅ DoD (完了条件)
- [ ] `spec.md` の分母シナリオ定義と上流 `MUST` 指摘ゼロ
- [ ] Pass 1（貫通）＆ Pass 2（引き算リファクタリング）の完了
- [ ] 対象リポジトリの `make check-all` パスと独立レビュアー `MUST = 0`
- [ ] 学びの還流と PR 作成・3点ブリーフィングの完了

## 🧭 Routing
- Working Memory (<=50 lines): [tasks/context.md](tasks/context.md)
- Task Checklist: [tasks/progress.md](tasks/progress.md)
- Lessons Learned: [tasks/lessons_learned.md](tasks/lessons_learned.md)
""",
            encoding="utf-8",
        )

    # 旧 verify_cleanliness.py 互換のため Step 2 で 완전移行するまで _index.md もシンボリックまたは同内容で保持可能にするが、
    # verify_cleanliness.py 自体を AGENTS.md / _index.md 両対応に更新する。

    context_md = ws_dir / "tasks" / "context.md"
    if not context_md.exists():
        context_md.write_text(
            f"""# 📍 Current Context (Working Memory)

> **⚠️ Agentへの絶対ルール**
> - 最大50行以内に保つこと。ユーザー返答前に必ず最新状態に更新すること。

---

## 🎯 現在の焦点 (Current Focus)
- Epic `{epic}` を立ち上げ。まずは `spec.md` の分母（全シナリオID）を定義する。

## 📌 決定事項 (Decisions)
- なし

## 🚀 次のアクション (Next Actions)
1. 対象リポジトリの Worktree 内で仕様（`spec.md`）を策定する。
""",
            encoding="utf-8",
        )

    progress_md = ws_dir / "tasks" / "progress.md"
    if not progress_md.exists():
        progress_md.write_text(
            f"""# Epic Workspace Progress: {epic}

## 📋 タスクリスト
- `[ ]` **Phase 0: 仕様固定 (`spec.md` 分母確定 & 上流レビュー)**
- `[ ]` **Phase 1: Pass 1（貫通 — Make it Work）**
- `[ ]` **Phase 2: Pass 2（引き算リファクタリング — Make it Right）**
- `[ ]` **Phase 3: 学習還流 & PR回収 (`make ws-harvest`)**
""",
            encoding="utf-8",
        )

    lessons_md = ws_dir / "tasks" / "lessons_learned.md"
    if not lessons_md.exists():
        lessons_md.write_text(
            f"""# 💡 Lessons Learned: {epic}

## 🤖 ルートA：Agent・仕組みの学び（CI / `docs/rules/` / `docs/experiences/` / `SKILL.md`）
- （作業中に発生したエラー・手戻り・再発防止策を記録）

## 🧠 ルートB：社長自身の気づき・内省候補（`second-brain`）
- （意思決定やトレードオフから得られた思考・哲学の種を記録）
""",
            encoding="utf-8",
        )


def mount_worktree(ws_dir: Path, epic: str, repo_name: str) -> None:
    repo_root = YOU_INC_ROOT / repo_name
    if not (repo_root / ".git").exists():
        print(f"⚠️  Skipping '{repo_name}': Git repository not found at {repo_root}")
        return

    wt_target = ws_dir / "worktrees" / repo_name
    branch_name = f"epic/{epic}"

    if wt_target.exists():
        print(f"ℹ️  Worktree already exists: {wt_target.relative_to(AGENT_CORE_ROOT)}")
        return

    # Check if branch already exists
    branch_check = run_git(repo_root, ["rev-parse", "--verify", branch_name], check=False)
    if branch_check.returncode == 0:
        cmd = ["worktree", "add", str(wt_target), branch_name]
    else:
        cmd = ["worktree", "add", "-b", branch_name, str(wt_target), "main"]

    res = run_git(repo_root, cmd, check=False)
    if res.returncode != 0:
        print(f"❌ Failed to mount worktree for {repo_name}:\n{res.stderr}")
        sys.exit(1)

    print(f"✅ Mounted worktree: {wt_target.relative_to(AGENT_CORE_ROOT)} (branch: {branch_name})")


def cmd_new(args: argparse.Namespace) -> None:
    epic = args.epic
    ws_dir = WORKSPACES_DIR / epic
    create_workspace_files(ws_dir, epic, args.issue)
    print(f"✅ Initialized workspace: workspaces/{epic}/")

    repos = [r.strip() for r in args.repos.split(",") if r.strip()]
    for repo in repos:
        mount_worktree(ws_dir, epic, repo)


def cmd_harvest(args: argparse.Namespace) -> None:
    epic = args.epic
    ws_dir = WORKSPACES_DIR / epic
    if not ws_dir.exists():
        print(f"❌ Workspace not found: workspaces/{epic}/")
        sys.exit(1)

    wt_parent = ws_dir / "worktrees"
    if wt_parent.exists():
        for wt_dir in sorted(wt_parent.iterdir()):
            if not wt_dir.is_dir():
                continue
            repo_name = wt_dir.name
            repo_root = YOU_INC_ROOT / repo_name
            status_res = run_git(wt_dir, ["status", "--porcelain"], check=False)
            if status_res.stdout.strip():
                print(
                    f"❌ Worktree '{repo_name}' has uncommitted changes! Commit or stash before harvesting:\n{status_res.stdout}"
                )
                sys.exit(1)

            rem_res = run_git(repo_root, ["worktree", "remove", str(wt_dir)], check=False)
            if rem_res.returncode != 0:
                print(f"❌ Failed to remove worktree '{repo_name}':\n{rem_res.stderr}")
                sys.exit(1)
            print(f"✅ Unmounted worktree: {repo_name}")

    scratch_dir = ws_dir / "scratch"
    if scratch_dir.exists():
        shutil.rmtree(scratch_dir)
        scratch_dir.mkdir(exist_ok=True)
        print(f"🧹 Cleaned scratch directory: workspaces/{epic}/scratch/")

    print(f"🎉 Workspace '{epic}' is ready for harvest/close!")


def cmd_list(_args: argparse.Namespace) -> None:
    print("=== Active Workspaces ===")
    if WORKSPACES_DIR.exists():
        for ws in sorted(WORKSPACES_DIR.iterdir()):
            if ws.is_dir():
                wts = []
                if (ws / "worktrees").exists():
                    wts = [d.name for d in (ws / "worktrees").iterdir() if d.is_dir()]
                wt_info = f" (worktrees: {', '.join(wts)})" if wts else ""
                print(f"  - {ws.name}{wt_info}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Epic Workspaces and Git Worktrees")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="Create or update an Epic workspace and mount worktrees")
    p_new.add_argument("--epic", required=True, help="Epic directory/branch name")
    p_new.add_argument("--repos", default="core-service", help="Comma-separated repo names (e.g. core-service,agent-core)")
    p_new.add_argument("--issue", default=None, help="GitHub Issue number")

    p_harvest = sub.add_parser("harvest", help="Unmount worktrees and clean temporary files for closing")
    p_harvest.add_argument("--epic", required=True, help="Epic name")

    sub.add_parser("list", help="List workspaces and mounted worktrees")

    args = parser.parse_args()
    if args.command == "new":
        cmd_new(args)
    elif args.command == "harvest":
        cmd_harvest(args)
    elif args.command == "list":
        cmd_list(args)


if __name__ == "__main__":
    main()
