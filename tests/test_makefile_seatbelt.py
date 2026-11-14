"""
Tests for Makefile Seatbelt Auto-Enforcement specification.
Covers scenarios [SC-SB-01] through [SC-SB-09].
"""
import inspect
import os
import subprocess
import sys
import unittest
from pathlib import Path

# tools ディレクトリを sys.path に追加
tools_dir = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(tools_dir))

import sandbox_runner


class TestMakefileSeatbelt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worktree_dir = Path(__file__).resolve().parent.parent

    def _get_clean_env(self, extra_vars=None):
        env = os.environ.copy()
        env.pop("YOU_INC_SANDBOX_ACTIVE", None)
        if extra_vars:
            env.update(extra_vars)
        return env

    def test_sc_sb_01_host_auto_sandbox_launch(self):
        """[SC-SB-01]: ホスト環境（YOU_INC_SANDBOX_ACTIVE 未設定）から make -n validate-tests を実行した際、出力に sandbox_runner.py --role worker が含まれ、自動的にサンドボックス経由で実行されるコマンド列が生成されること。"""
        env = self._get_clean_env()
        res = subprocess.run(
            ["make", "-n", "validate-tests"],
            cwd=self.worktree_dir,
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"make -n failed: {res.stderr}")
        self.assertIn("sandbox_runner.py", res.stdout)
        self.assertIn("--role worker", res.stdout)
        self.assertIn("--worktree", res.stdout)

    def test_sc_sb_02_sandbox_reentrancy_guard(self):
        """[SC-SB-02]: サンドボックス内（YOU_INC_SANDBOX_ACTIVE=1）から make -n check-all および make -n validate-tests を実行した際、sandbox_runner.py が含まれず、直接対応するスクリプト・テストコマンド（python -m unittest 等）が生成されること（再入ガード）。"""
        env = self._get_clean_env({"YOU_INC_SANDBOX_ACTIVE": "1"})

        # validate-tests の再入ガード検証
        res_tests = subprocess.run(
            ["make", "-n", "validate-tests"],
            cwd=self.worktree_dir,
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_tests.returncode, 0, f"make -n validate-tests failed: {res_tests.stderr}")
        self.assertNotIn("sandbox_runner.py", res_tests.stdout)
        self.assertIn("unittest", res_tests.stdout)

        # check-all の再入ガード検証
        res_check = subprocess.run(
            ["make", "-n", "check-all"],
            cwd=self.worktree_dir,
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_check.returncode, 0, f"make -n check-all failed: {res_check.stderr}")
        self.assertNotIn("sandbox_runner.py", res_check.stdout)
        self.assertIn("unittest", res_check.stdout)

    def test_sc_sb_03_idempotency_and_leave_no_trace(self):
        """[SC-SB-03]: make validate-tests の dry-run および実行が複数回行われても、一時ファイルの残存や副作用が発生せず、常に同一の決定論的結果となること（Leave No Trace・冪等性）。"""
        env_host = self._get_clean_env()
        env_sb = self._get_clean_env({"YOU_INC_SANDBOX_ACTIVE": "1"})

        # ホスト環境での複数回 dry-run 決定論的検証
        res1 = subprocess.run(
            ["make", "-n", "validate-tests"],
            cwd=self.worktree_dir,
            env=env_host,
            capture_output=True,
            text=True,
        )
        res2 = subprocess.run(
            ["make", "-n", "validate-tests"],
            cwd=self.worktree_dir,
            env=env_host,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res1.returncode, res2.returncode)
        self.assertEqual(res1.stdout, res2.stdout)
        self.assertEqual(res1.stderr, res2.stderr)

        # サンドボックス内環境での複数回 dry-run 決定論的検証
        res_sb1 = subprocess.run(
            ["make", "-n", "validate-tests"],
            cwd=self.worktree_dir,
            env=env_sb,
            capture_output=True,
            text=True,
        )
        res_sb2 = subprocess.run(
            ["make", "-n", "validate-tests"],
            cwd=self.worktree_dir,
            env=env_sb,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_sb1.returncode, res_sb2.returncode)
        self.assertEqual(res_sb1.stdout, res_sb2.stdout)
        self.assertEqual(res_sb1.stderr, res_sb2.stderr)

    def test_sc_sb_04_boundary_conditions(self):
        """[SC-SB-04]: ワークツリー境界および環境変数の境界値検証：
        (a) カレントディレクトリ（$(CURDIR)）が --worktree 引数に正確に反映されること。
        (b) YOU_INC_SANDBOX_ACTIVE="0"、空文字、未設定、"true"、"2" の場合、誤認されず確実にホスト側（sandbox_runner.py 経由）のコマンド列が生成されること（Fail-closed 境界値）。
        (c) sandbox_runner.is_inside_sandbox() は環境変数が "1" の完全一致でのみ True を返し、"0", "", None, "true" 等では False を返すこと。"""
        # (a) カレントディレクトリ反映検証
        env_host = self._get_clean_env()
        res_curdir = subprocess.run(
            ["make", "-n", "validate-tests"],
            cwd=self.worktree_dir,
            env=env_host,
            capture_output=True,
            text=True,
        )
        self.assertIn(str(self.worktree_dir), res_curdir.stdout)

        # (b) Fail-closed 境界値検証（"0", "", "true", "True", "2", "FALSE", "yes" など）
        boundary_values = ["0", "", "true", "True", "2", "FALSE", "yes"]
        for val in boundary_values:
            with self.subTest(boundary_val=val):
                env = self._get_clean_env({"YOU_INC_SANDBOX_ACTIVE": val})
                res = subprocess.run(
                    ["make", "-n", "validate-tests"],
                    cwd=self.worktree_dir,
                    env=env,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(res.returncode, 0, f"make -n failed for val='{val}': {res.stderr}")
                self.assertIn(
                    "sandbox_runner.py",
                    res.stdout,
                    f"YOU_INC_SANDBOX_ACTIVE='{val}' did not trigger host sandbox launcher (Fail-closed violation)",
                )

        # (c) sandbox_runner.is_inside_sandbox() の境界値検証
        self.assertTrue(
            hasattr(sandbox_runner, "SANDBOX_ENV_VAR"),
            "sandbox_runner.SANDBOX_ENV_VAR constant is missing",
        )
        self.assertEqual(
            sandbox_runner.SANDBOX_ENV_VAR,
            "YOU_INC_SANDBOX_ACTIVE",
            "SANDBOX_ENV_VAR value must be 'YOU_INC_SANDBOX_ACTIVE'",
        )
        self.assertTrue(
            hasattr(sandbox_runner, "is_inside_sandbox"),
            "sandbox_runner.is_inside_sandbox() function is missing",
        )

        original_env = os.environ.get("YOU_INC_SANDBOX_ACTIVE")
        try:
            # "1" のみ True
            os.environ["YOU_INC_SANDBOX_ACTIVE"] = "1"
            self.assertTrue(sandbox_runner.is_inside_sandbox())

            # それ以外はすべて False
            for non_one in ["0", "", "true", "True", "2", "FALSE", "yes"]:
                os.environ["YOU_INC_SANDBOX_ACTIVE"] = non_one
                self.assertFalse(
                    sandbox_runner.is_inside_sandbox(),
                    f"is_inside_sandbox() should return False for '{non_one}'",
                )

            # 未設定時も False
            if "YOU_INC_SANDBOX_ACTIVE" in os.environ:
                del os.environ["YOU_INC_SANDBOX_ACTIVE"]
            self.assertFalse(
                sandbox_runner.is_inside_sandbox(),
                "is_inside_sandbox() should return False when environment variable is unset",
            )
        finally:
            if original_env is not None:
                os.environ["YOU_INC_SANDBOX_ACTIVE"] = original_env
            elif "YOU_INC_SANDBOX_ACTIVE" in os.environ:
                del os.environ["YOU_INC_SANDBOX_ACTIVE"]

    def test_sc_sb_05_reconciliation_env_injection_and_isolation(self):
        """[SC-SB-05]: tools/sandbox_runner.py の run_in_sandbox は子プロセスの環境変数に YOU_INC_SANDBOX_ACTIVE="1" を注入し、親環境やホスト側の os.environ を破壊・残留させないこと（調停・透過伝播）。"""
        # シグネチャ検査: env パラメータが存在しデフォルト None であること
        sig = inspect.signature(sandbox_runner.run_in_sandbox)
        self.assertIn("env", sig.parameters, "run_in_sandbox missing 'env' parameter")
        self.assertIs(sig.parameters["env"].default, None)

        original_env_val = os.environ.get("YOU_INC_SANDBOX_ACTIVE")
        try:
            # サンドボックス内部にいない場合かつ macOS Seatbelt が利用可能な場合のみ実プロセス起動による注入・隔離検証
            if Path("/usr/bin/sandbox-exec").exists() and not getattr(sandbox_runner, "is_inside_sandbox", lambda: False)():
                custom_var = "TEST_CUSTOM_SB_05_VAL"
                test_command = [
                    sys.executable,
                    "-c",
                    "import os; print('ACTIVE=' + os.environ.get('YOU_INC_SANDBOX_ACTIVE', 'NONE')); print('CUSTOM=' + os.environ.get('TEST_CUSTOM_KEY', 'NONE'))",
                ]

                # env 引数なしの場合
                res_no_env = sandbox_runner.run_in_sandbox(
                    test_command,
                    worktree_dir=self.worktree_dir,
                    capture_output=True,
                )
                self.assertEqual(res_no_env.returncode, 0, f"run_in_sandbox failed: {res_no_env.stderr}")
                self.assertIn("ACTIVE=1", res_no_env.stdout)

                # custom env 渡した場合
                res_custom = sandbox_runner.run_in_sandbox(
                    test_command,
                    worktree_dir=self.worktree_dir,
                    env={"TEST_CUSTOM_KEY": custom_var},
                    capture_output=True,
                )
                self.assertEqual(res_custom.returncode, 0, f"run_in_sandbox failed: {res_custom.stderr}")
                self.assertIn("ACTIVE=1", res_custom.stdout)
                self.assertIn(f"CUSTOM={custom_var}", res_custom.stdout)

                # 親プロセスの os.environ が汚染されていないことの確認
                self.assertEqual(
                    os.environ.get("YOU_INC_SANDBOX_ACTIVE"),
                    original_env_val,
                    "Parent os.environ was modified by run_in_sandbox",
                )
                self.assertNotIn("TEST_CUSTOM_KEY", os.environ)
        finally:
            if original_env_val is not None:
                os.environ["YOU_INC_SANDBOX_ACTIVE"] = original_env_val
            elif "YOU_INC_SANDBOX_ACTIVE" in os.environ:
                del os.environ["YOU_INC_SANDBOX_ACTIVE"]

    def test_sc_sb_06_batch_launch_host_check_all(self):
        """[SC-SB-06]: ホスト環境から make -n check-all を実行した際、前提ターゲット（validate-skills 等）を個別多重起動せず、1回のみ sandbox_runner.py --role worker --worktree "$(CURDIR)" -- $(MAKE) check-all を実行するコマンド列となること（多重起動防止・一括保護）。"""
        env = self._get_clean_env()
        res = subprocess.run(
            ["make", "-n", "check-all"],
            cwd=self.worktree_dir,
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"make -n check-all failed: {res.stderr}")
        runner_count = res.stdout.count("sandbox_runner.py")
        self.assertEqual(
            runner_count,
            1,
            f"Expected exactly 1 invocation of sandbox_runner.py in host check-all, got {runner_count}:\n{res.stdout}",
        )
        self.assertIn("check-all", res.stdout)
        # 前提ターゲットとして個別のスクリプトがホスト側で直列実行されていないこと
        self.assertNotIn("tools/audit_skills.py", res.stdout)

    def test_sc_sb_07_exit_code_propagation(self):
        """[SC-SB-07]: テスト実行コマンドが失敗した場合（exit code != 0）、sandbox_runner.py および Makefile がその失敗終了コードを正確に呼び出し元へ伝播すること。"""
        # Makefile における異常終了コード伝播
        res_make_fail = subprocess.run(
            ["make", "non-existent-fail-target-07"],
            cwd=self.worktree_dir,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(res_make_fail.returncode, 0)

        # sandbox_runner.py CLI における非ゼロ終了コード伝播（macOS Seatbelt 利用可能時）
        if Path("/usr/bin/sandbox-exec").exists() and not getattr(sandbox_runner, "is_inside_sandbox", lambda: False)():
            res_sb_fail = subprocess.run(
                [
                    sys.executable,
                    str(tools_dir / "sandbox_runner.py"),
                    "--role",
                    "worker",
                    "--worktree",
                    str(self.worktree_dir),
                    "--",
                    sys.executable,
                    "-c",
                    "import sys; sys.exit(42)",
                ],
                cwd=self.worktree_dir,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                res_sb_fail.returncode,
                42,
                f"Expected exit code 42 from sandbox_runner, got {res_sb_fail.returncode}",
            )

    def test_sc_sb_08_domain_invariant_check_all_gates_order(self):
        """[SC-SB-08]: Makefile の check-all は、サンドボックス内において全品質ゲート（validate-skills, validate-orphans, validate-cleanliness, validate-links, validate-tests）を漏れなく同一順序で完走させること。"""
        env = self._get_clean_env({"YOU_INC_SANDBOX_ACTIVE": "1"})
        res = subprocess.run(
            ["make", "-n", "check-all"],
            cwd=self.worktree_dir,
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"make -n check-all failed: {res.stderr}")

        # 各品質ゲートの実行要素（スクリプトまたはターゲット名）が同一順序で完走することを検証
        expected_gate_markers = [
            ("validate-skills", "audit_skills.py"),
            ("validate-orphans", "audit_orphan_scripts.py"),
            ("validate-cleanliness", "verify_cleanliness.py"),
            ("validate-links", "check_markdown_links.py"),
            ("validate-tests", "unittest"),
        ]

        last_index = -1
        for gate_name, script_name in expected_gate_markers:
            # ターゲット名または実行スクリプトのいずれかが dry-run 出力に含まれていること
            idx_gate = res.stdout.find(gate_name)
            idx_script = res.stdout.find(script_name)
            idx = idx_gate if idx_gate != -1 else idx_script

            self.assertNotEqual(
                idx,
                -1,
                f"Gate '{gate_name}' ({script_name}) is missing from sandbox check-all dry-run output:\n{res.stdout}",
            )
            self.assertGreater(
                idx,
                last_index,
                f"Gate '{gate_name}' appeared out of order in check-all dry-run output:\n{res.stdout}",
            )
            last_index = idx

        # make -qp によるサンドボックス内 check-all の依存関係契約の検証
        res_db = subprocess.run(
            ["make", "-qp"],
            cwd=self.worktree_dir,
            env=env,
            capture_output=True,
            text=True,
        )
        check_all_dep_lines = [
            line for line in res_db.stdout.splitlines()
            if line.startswith("check-all:")
        ]
        self.assertTrue(
            any(
                all(g in line for g in ["validate-skills", "validate-orphans", "validate-cleanliness", "validate-links", "validate-tests"])
                for line in check_all_dep_lines
            ),
            f"check-all dependencies in sandbox mode do not contain all gates:\n{check_all_dep_lines}",
        )

    def test_sc_sb_09_test_alias_and_phony(self):
        """[SC-SB-09]: 公開インターフェース make test が validate-tests のエイリアスとして定義され、ホスト環境（sandbox_runner.py 経由）およびサンドボックス内（直接実行）の双方で validate-tests と等価に動作すること（.PHONY: test 含む）。"""
        # 1. ホスト環境での等価性検証
        env_host = self._get_clean_env()
        res_test_host = subprocess.run(
            ["make", "-n", "test"],
            cwd=self.worktree_dir,
            env=env_host,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_test_host.returncode, 0, f"make -n test failed: {res_test_host.stderr}")
        self.assertIn("sandbox_runner.py", res_test_host.stdout)
        self.assertIn("validate-tests", res_test_host.stdout)

        # 2. サンドボックス内環境での等価性検証
        env_sb = self._get_clean_env({"YOU_INC_SANDBOX_ACTIVE": "1"})
        res_test_sb = subprocess.run(
            ["make", "-n", "test"],
            cwd=self.worktree_dir,
            env=env_sb,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_test_sb.returncode, 0, f"make -n test in sandbox failed: {res_test_sb.stderr}")
        self.assertNotIn("sandbox_runner.py", res_test_sb.stdout)
        self.assertIn("unittest", res_test_sb.stdout)

        # 3. .PHONY: test の定義検証
        res_phony = subprocess.run(
            ["make", "-qp"],
            cwd=self.worktree_dir,
            capture_output=True,
            text=True,
        )
        phony_lines = [line for line in res_phony.stdout.splitlines() if line.startswith(".PHONY:")]
        test_in_phony = any("test" in line.split() for line in phony_lines)
        self.assertTrue(test_in_phony, f"Target 'test' is not declared in .PHONY:\n{phony_lines}")


if __name__ == "__main__":
    unittest.main()
