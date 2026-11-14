"""
Hermetic and Deterministic Unit/Integration Tests for workspace_manager.py.
Validates spec.md scenarios [SC-01] to [SC-10] and function contracts.
"""

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.workspace_manager as wm


def call_resolve_target_base(repo_root: Path, offline: bool = False) -> str:
    """Invokes resolve_target_base with contract assertion."""
    if not hasattr(wm, "resolve_target_base"):
        raise AssertionError("resolve_target_base is not implemented in tools.workspace_manager")
    return wm.resolve_target_base(repo_root, offline=offline)


def call_check_branch_divergence(
    repo_root: Path, branch_name: str, target_base: str
) -> tuple[bool, int, int]:
    """Invokes check_branch_divergence with contract assertion."""
    if not hasattr(wm, "check_branch_divergence"):
        raise AssertionError("check_branch_divergence is not implemented in tools.workspace_manager")
    return wm.check_branch_divergence(repo_root, branch_name, target_base)


def call_mount_worktree(
    ws_dir: Path,
    epic: str,
    repo_name: str,
    offline: bool = False,
    reset: bool = False,
) -> None:
    """Invokes mount_worktree with signature validation."""
    if not hasattr(wm, "mount_worktree"):
        raise AssertionError("mount_worktree is not implemented in tools.workspace_manager")
    try:
        return wm.mount_worktree(ws_dir, epic, repo_name, offline=offline, reset=reset)
    except TypeError as e:
        raise AssertionError(f"mount_worktree signature mismatch: {e}") from e


@contextlib.contextmanager
def capture_output():
    """Captures both stdout and stderr for inspecting logs and warning/error messages."""
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        yield stdout, stderr


class BaseWorkspaceManagerTestCase(unittest.TestCase):
    """Hermetic base test case managing isolated tempdir git repositories."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name).resolve()

        self.you_inc_root = self.temp_path / "you_inc"
        self.you_inc_root.mkdir(parents=True)

        self.ws_dir = self.you_inc_root / "agent-core" / "workspaces" / "test-workspace"
        self.ws_dir.mkdir(parents=True)

        # Patch roots in tools.workspace_manager to guarantee hermetic environment
        self.patcher_you_inc = patch.object(wm, "YOU_INC_ROOT", self.you_inc_root)
        self.patcher_agent_core = patch.object(
            wm, "AGENT_CORE_ROOT", self.you_inc_root / "agent-core"
        )
        self.patcher_you_inc.start()
        self.patcher_agent_core.start()

        # Sanitize Git environment against hook pollution (GIT_DIR, GIT_INDEX_FILE, etc.)
        git_leak_vars = [
            "GIT_DIR",
            "GIT_WORK_TREE",
            "GIT_INDEX_FILE",
            "GIT_OBJECT_DIRECTORY",
            "GIT_ALTERNATE_OBJECT_DIRECTORIES",
            "GIT_PREFIX",
        ]
        clean_env = {k: v for k, v in os.environ.items() if k not in git_leak_vars}
        self.patcher_environ = patch.dict(os.environ, clean_env, clear=True)
        self.patcher_environ.start()

        # Offline deterministic Git environment
        self.git_env = os.environ.copy()
        self.git_env["GIT_AUTHOR_NAME"] = "Test Author"
        self.git_env["GIT_AUTHOR_EMAIL"] = "author@example.com"
        self.git_env["GIT_COMMITTER_NAME"] = "Test Committer"
        self.git_env["GIT_COMMITTER_EMAIL"] = "committer@example.com"
        self.git_env["GIT_CONFIG_GLOBAL"] = "/dev/null"
        self.git_env["GIT_CONFIG_SYSTEM"] = "/dev/null"

    def tearDown(self) -> None:
        self.patcher_environ.stop()
        self.patcher_agent_core.stop()
        self.patcher_you_inc.stop()
        self.temp_dir.cleanup()

    def run_git(self, args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            env=self.git_env,
            check=True,
        )

    def commit_file(self, repo: Path, filename: str, content: str, msg: str) -> str:
        file_path = repo / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        self.run_git(["add", filename], cwd=repo)
        self.run_git(["commit", "-m", msg], cwd=repo)
        return self.get_head_hash(repo)

    def get_head_hash(self, repo: Path) -> str:
        return self.run_git(["rev-parse", "HEAD"], cwd=repo).stdout.strip()

    def get_ref_hash(self, repo: Path, ref: str) -> str:
        return self.run_git(["rev-parse", ref], cwd=repo).stdout.strip()

    def is_ancestor(self, ancestor_hash: str, commit_hash: str, repo: Path) -> bool:
        res = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor_hash, commit_hash],
            cwd=repo,
            env=self.git_env,
            capture_output=True,
        )
        return res.returncode == 0

    def setup_repo_with_remote(
        self, repo_name: str = "core-service"
    ) -> tuple[Path, Path, Path]:
        """
        Creates a bare origin remote, a seed clone, and a local working repository.
        All initialized at initial commit O1 on main.
        """
        bare_remote = self.temp_path / f"{repo_name}_origin.git"
        self.run_git(["init", "--bare", "-b", "main", str(bare_remote)], cwd=self.temp_path)

        seed_repo = self.temp_path / f"{repo_name}_seed"
        seed_repo.mkdir()
        self.run_git(["init", "-b", "main"], cwd=seed_repo)
        self.run_git(["remote", "add", "origin", str(bare_remote)], cwd=seed_repo)
        self.commit_file(seed_repo, "README.md", f"# {repo_name}", "Initial commit O1")
        self.run_git(["push", "-u", "origin", "main"], cwd=seed_repo)

        local_repo = self.you_inc_root / repo_name
        self.run_git(["clone", str(bare_remote), str(local_repo)], cwd=self.temp_path)
        return local_repo, bare_remote, seed_repo

    def setup_local_only_repo(self, repo_name: str = "core-service") -> Path:
        """Creates a repository without any remote origin."""
        local_repo = self.you_inc_root / repo_name
        local_repo.mkdir(parents=True)
        self.run_git(["init", "-b", "main"], cwd=local_repo)
        self.commit_file(local_repo, "README.md", f"# {repo_name}", "Initial local commit M1")
        return local_repo


class WorkspaceManagerScenarioTests(BaseWorkspaceManagerTestCase):
    """Test scenarios strictly mapped to spec.md [SC-01] through [SC-10]."""

    def test_sc01_happy_path_fetch_and_mount_origin_main(self) -> None:
        """
        [SC-01]: When ws-new is run on a repo with remote origin,
        'git fetch origin main' is performed and epic/<name> branch in worktree
        is created at origin/main, NOT local main.
        """
        local_repo, bare_remote, seed_repo = self.setup_repo_with_remote("core-service")

        # Push a new commit O2 to origin bare repo from seed clone
        o2_hash = self.commit_file(seed_repo, "remote_update.txt", "remote data", "Commit O2")
        self.run_git(["push", "origin", "main"], cwd=seed_repo)

        # Make an unpushed local commit L1 on local main
        l1_hash = self.commit_file(local_repo, "local_draft.txt", "local data", "Commit L1")

        # Verify initial local state: local main has L1, cached origin/main does NOT have O2
        self.assertEqual(self.get_head_hash(local_repo), l1_hash)

        # Run mount_worktree with offline=False (default behavior)
        with capture_output():
            call_mount_worktree(
                self.ws_dir, "sc01-test", "core-service", offline=False, reset=False
            )

        worktree_path = self.ws_dir / "worktrees" / "core-service"
        self.assertTrue(worktree_path.exists(), "Worktree directory should be created")

        worktree_head = self.get_head_hash(worktree_path)
        self.assertEqual(
            worktree_head,
            o2_hash,
            f"Worktree branch must point to origin/main commit {o2_hash}, but got {worktree_head}",
        )
        self.assertNotEqual(
            worktree_head,
            l1_hash,
            "Worktree branch must NOT point to unpushed local main commit L1",
        )
        self.assertFalse(
            self.is_ancestor(l1_hash, worktree_head, local_repo),
            "Unpushed local main commit L1 must not be in worktree history",
        )

    def test_sc02_happy_path_offline_uses_cached_origin_main(self) -> None:
        """
        [SC-02]: When --offline flag is specified, git fetch is skipped,
        and worktree is created from cached local origin/main.
        """
        local_repo, bare_remote, seed_repo = self.setup_repo_with_remote("core-service")
        cached_o1_hash = self.get_ref_hash(local_repo, "origin/main")

        # Remote receives a new commit O2, but local is offline so it won't be fetched
        o2_hash = self.commit_file(seed_repo, "feature.txt", "data", "Commit O2")
        self.run_git(["push", "origin", "main"], cwd=seed_repo)

        with capture_output():
            call_mount_worktree(
                self.ws_dir, "sc02-test", "core-service", offline=True, reset=False
            )

        worktree_path = self.ws_dir / "worktrees" / "core-service"
        self.assertTrue(worktree_path.exists())

        worktree_head = self.get_head_hash(worktree_path)
        self.assertEqual(
            worktree_head,
            cached_o1_hash,
            "Offline mode must use cached origin/main commit",
        )
        self.assertNotEqual(
            worktree_head,
            o2_hash,
            "Offline mode must NOT have fetched new commit O2 from remote",
        )
        self.assertEqual(
            self.get_ref_hash(local_repo, "origin/main"),
            cached_o1_hash,
            "Local origin/main ref must remain unchanged in offline mode",
        )

    def test_sc03_idempotency_reuse_identical_existing_branch(self) -> None:
        """
        [SC-03]: If local branch epic/<name> already exists and is identical
        to origin/main (ahead=0, behind=0), reuse it safely without blocking.
        """
        local_repo, bare_remote, seed_repo = self.setup_repo_with_remote("core-service")
        o1_hash = self.get_ref_hash(local_repo, "origin/main")

        # Create existing branch epic/sc03-test pointing exactly to o1_hash
        self.run_git(["branch", "epic/sc03-test", o1_hash], cwd=local_repo)

        with capture_output() as (stdout, stderr):
            call_mount_worktree(
                self.ws_dir, "sc03-test", "core-service", offline=True, reset=False
            )

        worktree_path = self.ws_dir / "worktrees" / "core-service"
        self.assertTrue(worktree_path.exists())
        self.assertEqual(self.get_head_hash(worktree_path), o1_hash)

    def test_sc04_boundary_local_main_ahead_does_not_pollute_worktree(self) -> None:
        """
        [SC-04]: When local main is ahead of origin/main (ahead > 0), ws-new creates
        epic/<name> strictly at origin/main without local main's unpushed commits.
        """
        local_repo, bare_remote, seed_repo = self.setup_repo_with_remote("core-service")
        o1_hash = self.get_ref_hash(local_repo, "origin/main")

        # Make two unpushed commits on local main
        l1_hash = self.commit_file(local_repo, "l1.txt", "1", "Commit L1")
        l2_hash = self.commit_file(local_repo, "l2.txt", "2", "Commit L2")

        with capture_output():
            call_mount_worktree(
                self.ws_dir, "sc04-test", "core-service", offline=True, reset=False
            )

        worktree_path = self.ws_dir / "worktrees" / "core-service"
        worktree_head = self.get_head_hash(worktree_path)

        self.assertEqual(worktree_head, o1_hash)
        self.assertFalse(self.is_ancestor(l1_hash, worktree_head, local_repo))
        self.assertFalse(self.is_ancestor(l2_hash, worktree_head, local_repo))

    def test_sc05_reconciliation_reset_diverged_existing_branch(self) -> None:
        """
        [SC-05]: When existing branch epic/<name> has diverged and --reset is given,
        force-reset branch to origin/main and mount worktree successfully.
        """
        local_repo, bare_remote, seed_repo = self.setup_repo_with_remote("core-service")
        o1_hash = self.get_ref_hash(local_repo, "origin/main")

        # Create diverged branch epic/sc05-test with commit D1
        self.run_git(["checkout", "-b", "epic/sc05-test"], cwd=local_repo)
        d1_hash = self.commit_file(local_repo, "diverged.txt", "diverged", "Commit D1")
        self.run_git(["checkout", "main"], cwd=local_repo)
        self.assertNotEqual(d1_hash, o1_hash)

        # Call mount_worktree with reset=True
        with capture_output():
            call_mount_worktree(
                self.ws_dir, "sc05-test", "core-service", offline=True, reset=True
            )

        worktree_path = self.ws_dir / "worktrees" / "core-service"
        self.assertTrue(worktree_path.exists())

        worktree_head = self.get_head_hash(worktree_path)
        self.assertEqual(
            worktree_head,
            o1_hash,
            "Diverged branch should be reset to origin/main commit",
        )
        self.assertEqual(self.get_ref_hash(local_repo, "epic/sc05-test"), o1_hash)

    def test_sc06_fault_tolerance_block_diverged_branch_without_reset(self) -> None:
        """
        [SC-06]: When existing branch epic/<name> has diverged and --reset is False,
        safely block by exiting with code 1, leaving the existing branch intact.
        """
        local_repo, bare_remote, seed_repo = self.setup_repo_with_remote("core-service")
        o1_hash = self.get_ref_hash(local_repo, "origin/main")

        # Create diverged branch epic/sc06-test with commit D1
        self.run_git(["checkout", "-b", "epic/sc06-test"], cwd=local_repo)
        d1_hash = self.commit_file(local_repo, "diverged.txt", "diverged", "Commit D1")
        self.run_git(["checkout", "main"], cwd=local_repo)

        with capture_output() as (stdout, stderr):
            with self.assertRaises(SystemExit) as cm:
                call_mount_worktree(
                    self.ws_dir, "sc06-test", "core-service", offline=True, reset=False
                )
            self.assertEqual(cm.exception.code, 1, "Should exit with code 1 on divergence")

        combined_logs = stdout.getvalue() + stderr.getvalue()
        self.assertIn(
            "Branch 'epic/sc06-test' already exists and has diverged from origin/main",
            combined_logs,
            "Error message must specify diverged branch and target_base",
        )
        self.assertIn(
            "Use --reset to overwrite or delete it manually.",
            combined_logs,
            "Error message must guide user to use --reset",
        )

        # Invariant: existing branch must not be destroyed
        self.assertEqual(
            self.get_ref_hash(local_repo, "epic/sc06-test"),
            d1_hash,
            "Diverged branch ref must remain intact when blocked",
        )

    def test_sc07_fault_tolerance_fetch_failure_fallback_to_cached_origin_main(self) -> None:
        """
        [SC-07]: If git fetch origin main fails (e.g. unreachable remote),
        log a warning and fall back to local cached origin/main.
        """
        local_repo, bare_remote, seed_repo = self.setup_repo_with_remote("core-service")
        cached_o1_hash = self.get_ref_hash(local_repo, "origin/main")

        # Break remote origin URL so fetch will fail
        self.run_git(
            ["remote", "set-url", "origin", str(self.temp_path / "broken_unreachable.git")],
            cwd=local_repo,
        )

        with capture_output() as (stdout, stderr):
            call_mount_worktree(
                self.ws_dir, "sc07-test", "core-service", offline=False, reset=False
            )

        combined_logs = stdout.getvalue() + stderr.getvalue()
        self.assertIn(
            "Failed to fetch 'origin/main'",
            combined_logs,
            "Warning must report fetch failure",
        )
        self.assertIn(
            "Falling back to cached 'origin/main'",
            combined_logs,
            "Warning must report fallback to cached origin/main",
        )

        worktree_path = self.ws_dir / "worktrees" / "core-service"
        self.assertTrue(worktree_path.exists())
        self.assertEqual(self.get_head_hash(worktree_path), cached_o1_hash)

    def test_sc08_fault_tolerance_no_origin_fallback_to_local_main(self) -> None:
        """
        [SC-08]: In a repository without origin remote, log a warning and fall back
        to local main as target base.
        """
        local_repo = self.setup_local_only_repo("core-service")
        m1_hash = self.get_head_hash(local_repo)

        with capture_output() as (stdout, stderr):
            call_mount_worktree(
                self.ws_dir, "sc08-test", "core-service", offline=False, reset=False
            )

        combined_logs = stdout.getvalue() + stderr.getvalue()
        self.assertIn(
            "'origin/main' not found for repository 'core-service'. Falling back to local 'main'.",
            combined_logs,
            "Warning must report missing origin/main and fallback to local main",
        )

        worktree_path = self.ws_dir / "worktrees" / "core-service"
        self.assertTrue(worktree_path.exists())
        self.assertEqual(self.get_head_hash(worktree_path), m1_hash)

    def test_sc09_domain_invariant_origin_main_priority(self) -> None:
        """
        [SC-09]: Domain invariant - unpushed local main commits must NEVER pollute
        a new epic branch whenever origin/main exists.
        """
        local_repo, bare_remote, seed_repo = self.setup_repo_with_remote("core-service")
        o1_hash = self.get_ref_hash(local_repo, "origin/main")

        # Make local main diverge significantly
        self.commit_file(local_repo, "unpushed_local_1.txt", "v1", "Local 1")
        self.commit_file(local_repo, "unpushed_local_2.txt", "v2", "Local 2")

        # resolve_target_base must return 'origin/main' regardless of local main changes
        resolved_offline = call_resolve_target_base(local_repo, offline=True)
        self.assertEqual(resolved_offline, "origin/main")

        # check_branch_divergence must detect divergence correctly
        is_diverged, ahead, behind = call_check_branch_divergence(
            local_repo, "main", "origin/main"
        )
        self.assertTrue(is_diverged)
        self.assertEqual(ahead, 2)
        self.assertEqual(behind, 0)

        # Worktree mounted must strictly resolve to origin/main
        with capture_output():
            call_mount_worktree(
                self.ws_dir, "sc09-test", "core-service", offline=True, reset=False
            )
        worktree_head = self.get_head_hash(self.ws_dir / "worktrees" / "core-service")
        self.assertEqual(worktree_head, o1_hash)

    def test_sc10_executive_secretary_skill_spec(self) -> None:
        """
        [SC-10]: skills/orchestrators/executive-secretary/SKILL.md must not exceed 80 lines,
        and must require checking 'git diff origin/main..HEAD' before PR creation.
        """
        skill_file = (
            Path(wm.__file__).resolve().parent.parent
            / "skills"
            / "orchestrators"
            / "executive-secretary"
            / "SKILL.md"
        )
        self.assertTrue(skill_file.exists(), f"SKILL.md not found at {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        lines = content.splitlines()

        self.assertLessEqual(
            len(lines),
            80,
            f"SKILL.md line count must be <= 80 lines (current: {len(lines)})",
        )
        self.assertIn(
            "git diff origin/main..HEAD",
            content,
            "SKILL.md must document 'git diff origin/main..HEAD' verification before PR creation",
        )


class WorkspaceManagerFunctionContractTests(BaseWorkspaceManagerTestCase):
    """Direct contract tests for public internal functions and CLI flags."""

    def test_unit_resolve_target_base_no_ref_raises_runtime_error(self) -> None:
        """resolve_target_base must raise RuntimeError if neither origin/main nor main exists."""
        empty_repo = self.temp_path / "empty_repo"
        empty_repo.mkdir()
        self.run_git(["init", "-b", "dev-only"], cwd=empty_repo)
        self.commit_file(empty_repo, "file.txt", "content", "initial commit on dev-only")

        with self.assertRaises(RuntimeError):
            call_resolve_target_base(empty_repo, offline=True)

    def test_unit_check_branch_divergence_matrix(self) -> None:
        """check_branch_divergence returns (is_diverged, ahead, behind) accurately."""
        local_repo, bare_remote, seed_repo = self.setup_repo_with_remote("core-service")

        # 1. Identical: (False, 0, 0)
        self.run_git(["branch", "identical-branch", "origin/main"], cwd=local_repo)
        div, ahead, behind = call_check_branch_divergence(
            local_repo, "identical-branch", "origin/main"
        )
        self.assertFalse(div)
        self.assertEqual((ahead, behind), (0, 0))

        # 2. Ahead: (True, 1, 0)
        self.run_git(["checkout", "-b", "ahead-branch", "origin/main"], cwd=local_repo)
        self.commit_file(local_repo, "ahead.txt", "data", "Ahead commit")
        self.run_git(["checkout", "main"], cwd=local_repo)
        div, ahead, behind = call_check_branch_divergence(
            local_repo, "ahead-branch", "origin/main"
        )
        self.assertTrue(div)
        self.assertEqual((ahead, behind), (1, 0))

        # 3. Behind: (True, 0, 1)
        # Push commit to bare remote and fetch into origin/main
        self.commit_file(seed_repo, "remote.txt", "data", "Remote commit")
        self.run_git(["push", "origin", "main"], cwd=seed_repo)
        self.run_git(["fetch", "origin", "main"], cwd=local_repo)
        # identical-branch is now behind origin/main by 1
        div, ahead, behind = call_check_branch_divergence(
            local_repo, "identical-branch", "origin/main"
        )
        self.assertTrue(div)
        self.assertEqual((ahead, behind), (0, 1))

        # 4. Diverged (both ahead and behind): (True, 1, 1)
        div, ahead, behind = call_check_branch_divergence(
            local_repo, "ahead-branch", "origin/main"
        )
        self.assertTrue(div)
        self.assertEqual((ahead, behind), (1, 1))

    def test_mount_worktree_no_ref_exits_1(self) -> None:
        """mount_worktree exits with code 1 if neither origin/main nor main can be resolved."""
        repo_dir = self.you_inc_root / "empty-repo"
        repo_dir.mkdir(parents=True)
        self.run_git(["init", "-b", "custom-branch"], cwd=repo_dir)
        self.commit_file(repo_dir, "custom.txt", "data", "Commit")

        with capture_output() as (stdout, stderr):
            with self.assertRaises(SystemExit) as cm:
                call_mount_worktree(
                    self.ws_dir, "test-epic", "empty-repo", offline=True, reset=False
                )
            self.assertEqual(cm.exception.code, 1)

        combined_logs = stdout.getvalue() + stderr.getvalue()
        self.assertIn(
            "Neither 'origin/main' nor 'main' could be resolved for repository 'empty-repo'.",
            combined_logs,
        )

    def test_cli_argparse_offline_and_reset_flags(self) -> None:
        """CLI `new` subcommand accepts --offline and --reset flags."""
        script_path = Path(wm.__file__).resolve()
        res = subprocess.run(
            [sys.executable, str(script_path), "new", "--help"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn(
            "--offline",
            res.stdout,
            "CLI help for `new` must include `--offline` flag",
        )
        self.assertIn(
            "--reset",
            res.stdout,
            "CLI help for `new` must include `--reset` flag",
        )


if __name__ == "__main__":
    unittest.main()
