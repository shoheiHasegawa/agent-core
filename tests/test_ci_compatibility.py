import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

# tools ディレクトリを sys.path に追加
tools_dir = Path(__file__).resolve().parent.parent / "tools"
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

import audit_skills
import check_markdown_links


class TestCiCompatibility(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent

    def test_sc_01_verify_gemini_identity_monorepo_success(self):
        """[SC-01]: モノレポ環境（通常配置および Worktree 階層配下）で root/GEMINI.md と agent-core/GEMINI.md が完全一致する場合、verify_gemini_identity(agent_core_root) が []（エラーなし）を返すこと。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            gemini_content = "# Global Constitution: GEMINI.md\nContent here."

            # Case A: 通常配置
            mono_root_a = Path(tmpdir) / "mono_a"
            mono_root_a.mkdir(parents=True, exist_ok=True)
            (mono_root_a / "GEMINI.md").write_text(gemini_content, encoding="utf-8")

            agent_core_a = mono_root_a / "agent-core"
            agent_core_a.mkdir(parents=True, exist_ok=True)
            (agent_core_a / "GEMINI.md").write_text(gemini_content, encoding="utf-8")

            errors_a = audit_skills.verify_gemini_identity(agent_core_a)
            self.assertEqual(errors_a, [])

            # Case B: Worktree 階層配下
            mono_root_b = Path(tmpdir) / "mono_b"
            mono_root_b.mkdir(parents=True, exist_ok=True)
            (mono_root_b / "GEMINI.md").write_text(gemini_content, encoding="utf-8")

            agent_core_b = mono_root_b / "agent-core"
            agent_core_b.mkdir(parents=True, exist_ok=True)
            (agent_core_b / "GEMINI.md").write_text(gemini_content, encoding="utf-8")

            wt_b = agent_core_b / "workspaces" / "epic" / "worktrees" / "agent-core"
            wt_b.mkdir(parents=True, exist_ok=True)
            (wt_b / "GEMINI.md").write_text(gemini_content, encoding="utf-8")

            errors_b = audit_skills.verify_gemini_identity(wt_b)
            self.assertEqual(errors_b, [])

    def test_sc_02_verify_gemini_identity_standalone_success(self):
        """[SC-02]: 単体 checkout 環境（親階層に GEMINI.md も兄弟リポも存在しない）で agent-core/GEMINI.md が存在し非空である場合、verify_gemini_identity(agent_core_root) が []（エラーなし）を返すこと。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            standalone_root = Path(tmpdir) / "standalone-agent-core"
            standalone_root.mkdir(parents=True, exist_ok=True)
            gemini_content = "# Agent-Core Local Constitution"
            (standalone_root / "GEMINI.md").write_text(gemini_content, encoding="utf-8")

            errors = audit_skills.verify_gemini_identity(standalone_root)
            self.assertEqual(errors, [])

    def test_sc_03_check_markdown_links_standalone_cross_repo_skipped(self):
        """[SC-03]: 単体 checkout 環境の check_markdown_links(repo_root) において、リポジトリ内部リンクがすべて実在する場合、モノレポ横断相対リンク（../../core-service/... 等）が含まれていても []（エラーなし）を返すこと。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "standalone-agent-core"
            repo_root.mkdir(parents=True, exist_ok=True)

            docs_dir = repo_root / "docs"
            docs_dir.mkdir(parents=True, exist_ok=True)
            (docs_dir / "guide.md").write_text("# Guide", encoding="utf-8")

            readme_content = """# README
- [Local Guide](docs/guide.md)
- [Cross Repo Service](../../core-service/README.md)
- [Cross Monorepo Constitution](../../GEMINI.md)
- [Cross Second Brain](../second-brain/00_Inbox/memo.md)
"""
            (repo_root / "README.md").write_text(readme_content, encoding="utf-8")

            errors = check_markdown_links.check_markdown_links(repo_root)
            self.assertEqual(errors, [])

    def test_sc_04_ci_workflow_runs_unittest_and_gates(self):
        """[SC-04]: .github/workflows/ci.yml に python3 -m unittest discover -s tests -p "test_*.py" および既存4種の実行が含まれていること。"""
        ci_path = self.repo_root / ".github" / "workflows" / "ci.yml"
        self.assertTrue(ci_path.exists(), f"CI workflow file not found at {ci_path}")
        content = ci_path.read_text(encoding="utf-8")

        expected_commands = [
            "python3 tools/audit_skills.py",
            "python3 tools/audit_orphan_scripts.py",
            "python3 tools/verify_cleanliness.py",
            "python3 tools/check_markdown_links.py",
            'python3 -m unittest discover -s tests -p "test_*.py"',
        ]
        for cmd in expected_commands:
            self.assertIn(
                cmd,
                content,
                f"Required quality gate command '{cmd}' missing from .github/workflows/ci.yml",
            )

    def test_sc_05_idempotency_multiple_runs_unchanged(self):
        """[SC-05]: verify_gemini_identity および check_markdown_links を同一ディレクトリに対して複数回連続実行しても、ファイル変更を行わず常に同一のエラーリストを返すこと。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "agent-core"
            test_dir.mkdir(parents=True, exist_ok=True)
            (test_dir / "GEMINI.md").write_text("# GEMINI", encoding="utf-8")
            (test_dir / "README.md").write_text("[Guide](missing.md)", encoding="utf-8")

            def get_dir_state(p: Path):
                state = {}
                for f in sorted(p.rglob("*")):
                    if f.is_file():
                        state[str(f.relative_to(p))] = (
                            f.stat().st_mtime,
                            hashlib.sha256(f.read_bytes()).hexdigest(),
                        )
                return state

            state_before = get_dir_state(test_dir)

            res_gemini_1 = audit_skills.verify_gemini_identity(test_dir)
            res_gemini_2 = audit_skills.verify_gemini_identity(test_dir)
            self.assertEqual(res_gemini_1, res_gemini_2)

            res_links_1 = check_markdown_links.check_markdown_links(test_dir)
            res_links_2 = check_markdown_links.check_markdown_links(test_dir)
            self.assertEqual(res_links_1, res_links_2)

            state_after = get_dir_state(test_dir)
            self.assertEqual(
                {k: v[1] for k, v in state_before.items()},
                {k: v[1] for k, v in state_after.items()},
                "File contents changed during validation runs",
            )

    def test_sc_06_worktree_path_not_excluded_and_internal_dirs_excluded(self):
        """[SC-06]: 親ディレクトリ名に workspaces と worktrees を含むパス配下で check_markdown_links(repo_root) を実行した際、リポジトリ内の .md ファイルが誤って除外されず検査対象となり、壊れたリンクが検知されること。またリポジトリ内の workspaces/ や scratch/ 配下の .md は除外されること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 親パスに workspaces と worktrees を含む構造
            repo_root = (
                Path(tmpdir)
                / "agent-core"
                / "workspaces"
                / "test-epic"
                / "worktrees"
                / "agent-core"
            )
            repo_root.mkdir(parents=True, exist_ok=True)

            docs_dir = repo_root / "docs"
            docs_dir.mkdir(parents=True, exist_ok=True)
            (docs_dir / "valid.md").write_text("# Valid Doc", encoding="utf-8")
            (docs_dir / "broken.md").write_text(
                "# Broken Doc\n[Broken Link](missing_internal.md)",
                encoding="utf-8",
            )

            # 除外対象ディレクトリ配下のファイル（壊れたリンクを含む）
            scratch_dir = repo_root / "scratch"
            scratch_dir.mkdir(parents=True, exist_ok=True)
            (scratch_dir / "temp.md").write_text(
                "# Scratch Doc\n[Broken Scratch](missing_scratch.md)",
                encoding="utf-8",
            )

            ws_dir = repo_root / "workspaces" / "sub_epic"
            ws_dir.mkdir(parents=True, exist_ok=True)
            (ws_dir / "ws_doc.md").write_text(
                "# Workspace Doc\n[Broken WS](missing_ws.md)",
                encoding="utf-8",
            )

            gemini_hidden = repo_root / ".gemini"
            gemini_hidden.mkdir(parents=True, exist_ok=True)
            (gemini_hidden / "hidden.md").write_text(
                "# Hidden Doc\n[Broken Hidden](missing_hidden.md)",
                encoding="utf-8",
            )

            errors = check_markdown_links.check_markdown_links(repo_root)

            # docs/broken.md の壊れたリンクのみが検知され、scratchやworkspaces内のリンクは無視されること
            self.assertTrue(
                any("docs/broken.md" in err and "missing_internal.md" in err for err in errors),
                f"Broken link in docs/broken.md not detected: {errors}",
            )
            self.assertFalse(
                any("scratch/temp.md" in err for err in errors),
                f"scratch/temp.md should be excluded: {errors}",
            )
            self.assertFalse(
                any("workspaces/sub_epic/ws_doc.md" in err for err in errors),
                f"workspaces directory should be excluded: {errors}",
            )
            self.assertFalse(
                any(".gemini/hidden.md" in err for err in errors),
                f".gemini directory should be excluded: {errors}",
            )

    def test_sc_07_monorepo_cross_repo_link_resolution(self):
        """[SC-07]: モノレポ環境（Worktree 配下を含む）で check_markdown_links(repo_root) を実行した際、モノレポ横断相対リンクがモノレポ正規配置基準（monorepo_root/agent-core/...）で検証され、実在すれば []、不在または monorepo_root 外への脱出であればエラーリストに検知されること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            mono_root = Path(tmpdir) / "monorepo"
            mono_root.mkdir(parents=True, exist_ok=True)

            (mono_root / "GEMINI.md").write_text("# Constitution", encoding="utf-8")

            cs_dir = mono_root / "core-service"
            cs_dir.mkdir(parents=True, exist_ok=True)
            (cs_dir / "README.md").write_text("# Core Service", encoding="utf-8")

            # 本体の agent-core
            agent_core = mono_root / "agent-core"
            agent_core.mkdir(parents=True, exist_ok=True)

            # Worktree 配下の agent-core
            wt_root = agent_core / "workspaces" / "epic" / "worktrees" / "agent-core"
            docs_dir = wt_root / "docs"
            docs_dir.mkdir(parents=True, exist_ok=True)

            # 正常リンク（agent-core/docs から見て ../../core-service/README.md, ../../GEMINI.md）
            (docs_dir / "valid_cross.md").write_text(
                "# Valid Cross\n"
                "- [Core Service](../../core-service/README.md)\n"
                "- [Root Constitution](../../GEMINI.md)\n",
                encoding="utf-8",
            )

            # 壊れたリンク（不在ファイル & モノレポルート外脱出）
            (docs_dir / "broken_cross.md").write_text(
                "# Broken Cross\n"
                "- [Missing Cross](../../core-service/missing_file.md)\n"
                "- [Escaping Cross](../../../outside_monorepo.md)\n",
                encoding="utf-8",
            )

            errors = check_markdown_links.check_markdown_links(wt_root)

            # valid_cross.md のリンクはエラーにならないこと
            self.assertFalse(
                any("valid_cross.md" in err for err in errors),
                f"Valid cross-repo links should not error: {errors}",
            )

            # broken_cross.md の2件がエラー検知されること
            self.assertTrue(
                any("missing_file.md" in err for err in errors),
                f"Missing cross-repo link not detected: {errors}",
            )
            self.assertTrue(
                any("outside_monorepo.md" in err for err in errors),
                f"Escaped monorepo link not detected: {errors}",
            )

    def test_sc_08_verify_gemini_identity_fault_tolerance(self):
        """[SC-08]: 以下のいずれかが発生した場合、verify_gemini_identity が非空のエラーリストを返すこと：
        1. モノレポ環境で root/GEMINI.md と agent-core/GEMINI.md が不一致。
        2. 兄弟リポが並ぶモノレポ親で root/GEMINI.md が欠損。
        3. root_gemini_path が明示指定されたのに存在しない。
        4. agent-core/GEMINI.md が不在、または空白文字のみ（空）。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # 1. モノレポ環境で root/GEMINI.md と agent-core/GEMINI.md が不一致
            with self.subTest(scenario="mismatch"):
                mono1 = base / "mono1"
                mono1.mkdir(parents=True, exist_ok=True)
                (mono1 / "GEMINI.md").write_text("# Root Content A", encoding="utf-8")
                ac1 = mono1 / "agent-core"
                ac1.mkdir(parents=True, exist_ok=True)
                (ac1 / "GEMINI.md").write_text("# Agent Content B", encoding="utf-8")

                errs1 = audit_skills.verify_gemini_identity(ac1)
                self.assertTrue(len(errs1) > 0, "Expected mismatch errors but got none")
                self.assertTrue(
                    any("mismatch" in e.lower() or "not match" in e.lower() for e in errs1),
                    f"Mismatch error message unexpected: {errs1}",
                )

            # 2. 兄弟リポが並ぶモノレポ親で root/GEMINI.md が欠損
            with self.subTest(scenario="missing_root_in_monorepo"):
                mono2 = base / "mono2"
                mono2.mkdir(parents=True, exist_ok=True)
                # GEMINI.md は作成しない
                (mono2 / "core-service").mkdir(parents=True, exist_ok=True)
                ac2 = mono2 / "agent-core"
                ac2.mkdir(parents=True, exist_ok=True)
                (ac2 / "GEMINI.md").write_text("# Agent Content", encoding="utf-8")

                errs2 = audit_skills.verify_gemini_identity(ac2)
                self.assertTrue(len(errs2) > 0, "Expected missing root GEMINI.md error")
                self.assertTrue(
                    any("Root GEMINI.md not found" in e for e in errs2),
                    f"Missing root GEMINI.md message unexpected: {errs2}",
                )

            # 3. root_gemini_path が明示指定されたのに存在しない
            with self.subTest(scenario="explicit_missing_root"):
                ac3 = base / "ac3"
                ac3.mkdir(parents=True, exist_ok=True)
                (ac3 / "GEMINI.md").write_text("# Agent Content", encoding="utf-8")
                non_existent = base / "non_existent_GEMINI.md"

                errs3 = audit_skills.verify_gemini_identity(ac3, root_gemini_path=non_existent)
                self.assertTrue(len(errs3) > 0, "Expected missing explicit root GEMINI.md error")
                self.assertTrue(
                    any("Root GEMINI.md not found" in e for e in errs3),
                    f"Missing explicit root GEMINI.md message unexpected: {errs3}",
                )

            # 4a. agent-core/GEMINI.md が不在
            with self.subTest(scenario="missing_agent_gemini"):
                ac4a = base / "ac4a"
                ac4a.mkdir(parents=True, exist_ok=True)
                errs4a = audit_skills.verify_gemini_identity(ac4a)
                self.assertTrue(len(errs4a) > 0, "Expected missing agent GEMINI.md error")
                self.assertTrue(
                    any("agent-core/GEMINI.md not found" in e for e in errs4a),
                    f"Missing agent GEMINI.md message unexpected: {errs4a}",
                )

            # 4b. agent-core/GEMINI.md が空白文字のみ（空）
            with self.subTest(scenario="empty_agent_gemini"):
                ac4b = base / "ac4b"
                ac4b.mkdir(parents=True, exist_ok=True)
                (ac4b / "GEMINI.md").write_text("   \n\t  \n", encoding="utf-8")
                errs4b = audit_skills.verify_gemini_identity(ac4b)
                self.assertTrue(len(errs4b) > 0, "Expected empty agent GEMINI.md error")
                self.assertTrue(
                    any("agent-core/GEMINI.md is empty" in e for e in errs4b),
                    f"Empty agent GEMINI.md message unexpected: {errs4b}",
                )

    def test_sc_09_standalone_internal_broken_link_detected(self):
        """[SC-09]: 単体 checkout 環境であっても、リポジトリ内部を指すリンク先が存在しない場合、check_markdown_links(repo_root) が非空のエラーリストを返すこと。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            standalone = Path(tmpdir) / "standalone-agent-core"
            standalone.mkdir(parents=True, exist_ok=True)
            (standalone / "README.md").write_text(
                "# Standalone Repo\n[Missing Internal Doc](docs/missing.md)",
                encoding="utf-8",
            )

            errors = check_markdown_links.check_markdown_links(standalone)
            self.assertTrue(len(errors) > 0, "Expected broken internal link error")
            self.assertTrue(
                any("README.md" in e and "docs/missing.md" in e for e in errors),
                f"Missing link not detected properly: {errors}",
            )

    def test_sc_10_find_monorepo_root_worktrees_boundary_and_gemini_invariance(self):
        """[SC-10]: worktrees/ ディレクトリ直下に agent-core/ と core-service/ の両方がマウントされた Worktree 環境であっても、find_monorepo_root は worktrees/ をモノレポルートと誤認せず、上位の真正なモノレポルートを返す（上位に存在しない場合は None を返す）こと。また agent-core/GEMINI.md 自体は変更されないこと。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Case A: 上位に真正モノレポが存在する場合
            mono = base / "true_monorepo"
            mono.mkdir(parents=True, exist_ok=True)
            (mono / "GEMINI.md").write_text("# True Root Constitution", encoding="utf-8")
            (mono / "agent-core").mkdir(parents=True, exist_ok=True)

            wt_dir = mono / "agent-core" / "workspaces" / "epic" / "worktrees"
            ac_wt = wt_dir / "agent-core"
            cs_wt = wt_dir / "core-service"
            ac_wt.mkdir(parents=True, exist_ok=True)
            cs_wt.mkdir(parents=True, exist_ok=True)

            resolved_root = audit_skills.find_monorepo_root(ac_wt)
            self.assertEqual(
                resolved_root,
                mono.resolve(),
                f"Expected true monorepo root {mono.resolve()}, but got {resolved_root}",
            )

            # Case B: 上位にモノレポ特徴が存在せず、孤立した worktrees ディレクトリの場合
            isolated_base = base / "isolated"
            iso_wt_dir = isolated_base / "worktrees"
            iso_ac = iso_wt_dir / "agent-core"
            iso_cs = iso_wt_dir / "core-service"
            iso_ac.mkdir(parents=True, exist_ok=True)
            iso_cs.mkdir(parents=True, exist_ok=True)

            iso_root = audit_skills.find_monorepo_root(iso_ac)
            self.assertIsNone(
                iso_root,
                f"worktrees/ directory should not be recognized as monorepo root, but got {iso_root}",
            )

        # Case C: agent-core/GEMINI.md の不変性確認（実ファイル）
        actual_gemini = self.repo_root / "GEMINI.md"
        self.assertTrue(actual_gemini.exists(), "agent-core/GEMINI.md must exist")
        gemini_text = actual_gemini.read_text(encoding="utf-8")
        self.assertTrue(len(gemini_text.strip()) > 0, "agent-core/GEMINI.md must not be empty")
        self.assertIn("Global Constitution: GEMINI.md", gemini_text)

    def test_sc_11_worktree_sibling_repo_link_resolution(self):
        """[SC-11]: worktrees/ 配下に兄弟リポジトリの Worktree が存在する環境では、他リポ横断リンクの検証に兄弟 Worktree 側の最新構造が優先使用されること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            mono = Path(tmpdir) / "monorepo"
            mono.mkdir(parents=True, exist_ok=True)
            (mono / "GEMINI.md").write_text("# Root", encoding="utf-8")

            # 本流の second-brain には旧ディレクトリ 10_Areas しかない状態
            (mono / "second-brain" / "10_Areas").mkdir(parents=True, exist_ok=True)

            wt_dir = mono / "agent-core" / "workspaces" / "epic" / "worktrees"
            ac_wt = wt_dir / "agent-core"
            sb_wt = wt_dir / "second-brain"
            (ac_wt / "docs").mkdir(parents=True, exist_ok=True)
            # Epic Worktree 側の second-brain は新ディレクトリ areas/ に移行済み
            (sb_wt / "areas").mkdir(parents=True, exist_ok=True)

            (ac_wt / "docs" / "arch.md").write_text(
                "- [Areas](../../second-brain/areas/)\n"
                "- [Root](../../GEMINI.md)\n",
                encoding="utf-8",
            )
            self.assertEqual(check_markdown_links.check_markdown_links(ac_wt), [])

            # 旧パスを参照し続けている場合は壊れたリンクとして検知すること
            (ac_wt / "docs" / "stale.md").write_text(
                "- [Old](../../second-brain/10_Areas/)\n",
                encoding="utf-8",
            )
            errors = check_markdown_links.check_markdown_links(ac_wt)
            self.assertTrue(any("10_Areas" in e for e in errors), f"Expected stale link error, got {errors}")


if __name__ == "__main__":
    unittest.main()
