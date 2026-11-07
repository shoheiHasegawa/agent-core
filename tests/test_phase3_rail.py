import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

# tools ディレクトリを sys.path に追加
tools_dir = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(tools_dir))

import audit_skills
import verify_cleanliness
import workspace_manager


class TestPhase3Rail(unittest.TestCase):
    def test_ac_ws_01_create_workspace_files_structure(self):
        """[AC-WS-01]: create_workspace_files 実行時に AGENTS.md, tasks/context.md, tasks/lessons_learned.md, scratch/, worktrees/ が作成され、docs/ と tasks/progress.md は作成されないこと。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            ws_dir = Path(tmpdir) / "test-epic"
            ws_dir.mkdir(parents=True, exist_ok=True)
            workspace_manager.create_workspace_files(ws_dir, "test-epic", "123")

            self.assertTrue((ws_dir / "AGENTS.md").exists())
            self.assertTrue((ws_dir / "tasks" / "context.md").exists())
            self.assertTrue((ws_dir / "tasks" / "lessons_learned.md").exists())
            self.assertTrue((ws_dir / "scratch").is_dir())
            self.assertTrue((ws_dir / "worktrees").is_dir())
            self.assertFalse((ws_dir / "docs").exists())
            self.assertFalse((ws_dir / "tasks" / "progress.md").exists())

            agents_content = (ws_dir / "AGENTS.md").read_text(encoding="utf-8")
            self.assertNotIn("progress.md", agents_content)

    def test_ac_ws_02_parse_review_verdict_pass(self):
        """[AC-WS-02]: parse_review_verdict において PASS かつ must=0 または must_count=0 が合格（True）と判定されること。"""
        report_xml = """# Review Report
Some findings.
<review_verdict status="PASS" must="0" should="1" imo="0" />
"""
        ok1, reason1 = workspace_manager.parse_review_verdict(report_xml)
        self.assertTrue(ok1)
        self.assertEqual(reason1, "OK")

        report_xml_alt = """# Review Report
<review_verdict status="PASS" must_count="0" should_count="2" imo_count="1" />
"""
        ok2, reason2 = workspace_manager.parse_review_verdict(report_xml_alt)
        self.assertTrue(ok2)
        self.assertEqual(reason2, "OK")

    def test_ac_ws_03_parse_review_verdict_anti_spoofing(self):
        """[AC-WS-03]: 自然言語のPASSやREJECT、must>0の場合は不合格（False）として判定されること。"""
        # 1. 自然言語の PASS のみ（構造化タグなし）
        report_spoof = "今回は PASS できません。修正が必要です。"
        ok1, _ = workspace_manager.parse_review_verdict(report_spoof)
        self.assertFalse(ok1)

        # 2. status="REJECT"
        report_reject = '<review_verdict status="REJECT" must="0" />'
        ok2, _ = workspace_manager.parse_review_verdict(report_reject)
        self.assertFalse(ok2)

        # 3. must="1"
        report_must_err = '<review_verdict status="PASS" must="1" />'
        ok3, _ = workspace_manager.parse_review_verdict(report_must_err)
        self.assertFalse(ok3)

        # 4. must_count="2"
        report_must_count_err = '<review_verdict status="PASS" must_count="2" />'
        ok4, _ = workspace_manager.parse_review_verdict(report_must_count_err)
        self.assertFalse(ok4)

    def test_ac_ws_04_find_unharvested_docs_protection(self):
        """[AC-WS-04]: Worktree 外に未回収の .md ドキュメントが残存している場合に検知されること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            ws_dir = Path(tmpdir)
            (ws_dir / "AGENTS.md").write_text("# Agents", encoding="utf-8")
            tasks_dir = ws_dir / "tasks"
            tasks_dir.mkdir()
            (tasks_dir / "context.md").write_text("# Context", encoding="utf-8")
            (tasks_dir / "lessons_learned.md").write_text("# Lessons", encoding="utf-8")
            (ws_dir / "scratch").mkdir()
            (ws_dir / "scratch" / "temp.md").write_text("# Scratch", encoding="utf-8")
            (ws_dir / "worktrees").mkdir()
            (ws_dir / "worktrees" / "repo_doc.md").write_text("# Repo Doc", encoding="utf-8")

            # 未回収ドキュメントなし（許可ファイルのみ）
            unharvested = workspace_manager.find_unharvested_docs(ws_dir)
            self.assertEqual(unharvested, [])

            # 未回収ドキュメント配置
            docs_dir = ws_dir / "docs"
            docs_dir.mkdir()
            stray_doc = docs_dir / "design.md"
            stray_doc.write_text("# Design", encoding="utf-8")
            stray_note = ws_dir / "notes.md"
            stray_note.write_text("# Notes", encoding="utf-8")

            found = workspace_manager.find_unharvested_docs(ws_dir)
            self.assertEqual(len(found), 2)
            found_names = {p.name for p in found}
            self.assertIn("design.md", found_names)
            self.assertIn("notes.md", found_names)

    def test_ac_aud_01_skill_line_limit_boundary(self):
        """[AC-AUD-01]: audit_skill_file において SKILL.md が80行以内なら合格、81行以上で行数超過エラーとなること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "test-skill"
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"

            # 80行（合格）
            content_80 = "---\nname: test\ndescription: test\n---\n" + "\n".join(f"Line {i}" for i in range(76))
            skill_file.write_text(content_80, encoding="utf-8")
            errs_80 = audit_skills.audit_skill_file(skill_file)
            self.assertEqual(errs_80, [])

            # 81行（不合格）
            content_81 = content_80 + "\nLine 77"
            skill_file.write_text(content_81, encoding="utf-8")
            errs_81 = audit_skills.audit_skill_file(skill_file)
            self.assertTrue(any("80" in e or "line" in e.lower() or "行" in e for e in errs_81))

    def test_ac_aud_02_gemini_identity_check(self):
        """[AC-AUD-02]: verify_gemini_identity において GEMINI.md が完全一致なら合格、差分があればエラーとなること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_dir = Path(tmpdir)
            agent_core_dir = root_dir / "agent-core"
            agent_core_dir.mkdir()

            root_gemini = root_dir / "GEMINI.md"
            agent_core_gemini = agent_core_dir / "GEMINI.md"

            root_gemini.write_text("Global Constitution\nLine 2", encoding="utf-8")
            agent_core_gemini.write_text("Global Constitution\nLine 2", encoding="utf-8")

            # 完全一致
            errs_match = audit_skills.verify_gemini_identity(agent_core_dir, root_gemini)
            self.assertEqual(errs_match, [])

            # 差分あり
            agent_core_gemini.write_text("Global Constitution\nLine 2 (Modified)", encoding="utf-8")
            errs_diff = audit_skills.verify_gemini_identity(agent_core_dir, root_gemini)
            self.assertTrue(len(errs_diff) > 0)

    def test_ac_cln_01_cleanliness_and_stale_workspace_check(self):
        """[AC-CLN-01]: verify_cleanliness が tasks/progress.md 不在でも警告を出さず、7日以上更新のないWorkspaceにstale_workspace警告を出力すること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            core_dir = Path(tmpdir)
            ws_dir = core_dir / "workspaces" / "stale-epic"
            ws_dir.mkdir(parents=True)
            agents_file = ws_dir / "AGENTS.md"
            agents_file.write_text("# Agents", encoding="utf-8")
            tasks_dir = ws_dir / "tasks"
            tasks_dir.mkdir()
            ctx_file = tasks_dir / "context.md"
            ctx_file.write_text("# Context", encoding="utf-8")

            # 8日前のタイムスタンプに設定
            old_time = time.time() - (8 * 86400)
            os.utime(agents_file, (old_time, old_time))
            os.utime(ctx_file, (old_time, old_time))

            errors, warnings = verify_cleanliness.check_cleanliness(core_dir)

            # tasks/progress.md 不在によるエラーや警告はないこと
            progress_warnings = [w for w in warnings if "progress.md" in str(w)]
            progress_errors = [e for e in errors if "progress.md" in str(e)]
            self.assertEqual(progress_warnings, [])
            self.assertEqual(progress_errors, [])

            # 7日以上前のWorkspaceに対する stale_workspace 警告が出力されること
            stale_warnings = [w for w in warnings if isinstance(w, dict) and w.get("type") == "stale_workspace"]
            self.assertTrue(len(stale_warnings) >= 1)


if __name__ == "__main__":
    unittest.main()
