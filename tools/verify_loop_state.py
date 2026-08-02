#!/usr/bin/env python3
"""verify_loop_state.py: SDD/TDDループの各フェーズ（Outer Red, Green, Quality Gate）の機械的判定ツール。

JSON-First Protocol (JSON-Out) に準拠し、終了コードと構造化JSONで合否判定を返却する。
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

# パス解決
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CORE_SERVICE_DIR = REPO_ROOT / "core-service"
AGENT_CORE_DIR = REPO_ROOT / "agent-core"


def run_command_capture(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        return 1, "", str(e)


def verify_outer_red(target_test: str | None = None) -> Dict[str, Any]:
    """Outer Red (結合テストが意図通り失敗すること) を検証する。

    合格条件:
    - pytest の終了コードが 1 (テスト失敗)
    - stdout/stderr に FAILED または AssertionError が含まれていること
    - 構文エラー (SyntaxError) や インポートエラー (ModuleNotFoundError) ではないこと
    """
    cmd = ["uv", "run", "pytest"]
    if target_test:
        cmd.append(target_test)
    else:
        cmd.append("tests/integration/")

    retcode, stdout, stderr = run_command_capture(cmd, CORE_SERVICE_DIR)
    combined = stdout + "\n" + stderr

    if retcode == 0:
        return {
            "success": False,
            "phase": "outer-red",
            "error": "Outer Red Failed: Tests PASSED unexpectedly. A new test scenario MUST fail initially before implementation.",
            "stdout": stdout,
        }

    # 構文エラーやインポートエラーの検知
    if "SyntaxError" in combined or "ModuleNotFoundError" in combined or "ImportError" in combined:
        return {
            "success": False,
            "phase": "outer-red",
            "error": "Outer Red Failed: Test file has syntax or import errors instead of a logical assertion failure.",
            "details": combined[-1000:],
        }

    if "FAILED" in combined or "AssertionError" in combined:
        return {
            "success": True,
            "phase": "outer-red",
            "message": "Outer Red Verified: Test scenario failed with expected assertion failure.",
            "summary": [line for line in combined.splitlines() if "FAILED" in line or "passed" in line][-5:],
        }

    return {
        "success": False,
        "phase": "outer-red",
        "error": f"Outer Red Failed: Test exited with code {retcode} but no standard assertion failure was detected.",
        "details": combined[-1000:],
    }


def verify_green(target_test: str | None = None) -> Dict[str, Any]:
    """Green (全テストが成功すること) を検証する。

    合格条件: pytest 終了コードが 0
    """
    cmd = ["uv", "run", "pytest"]
    if target_test:
        cmd.append(target_test)

    retcode, stdout, stderr = run_command_capture(cmd, CORE_SERVICE_DIR)
    combined = stdout + "\n" + stderr

    if retcode == 0:
        return {
            "success": True,
            "phase": "green",
            "message": "Green Verified: All specified tests passed successfully.",
            "summary": [line for line in combined.splitlines() if "passed" in line][-3:],
        }

    return {
        "success": False,
        "phase": "green",
        "error": "Green Failed: One or more tests failed.",
        "details": combined[-1500:],
    }


def verify_quality_gate() -> Dict[str, Any]:
    """Quality Gate (make check-all + validate_sdd.py + Coverage >= 90%) を検証する。"""
    # 1. make check-all
    retcode, stdout, stderr = run_command_capture(["uv", "run", "make", "check-all"], CORE_SERVICE_DIR)
    combined = stdout + "\n" + stderr

    if retcode != 0:
        return {
            "success": False,
            "phase": "quality",
            "error": "Quality Gate Failed: 'make check-all' failed.",
            "details": combined[-1500:],
        }

    # 2. validate_sdd.py
    validate_script = AGENT_CORE_DIR / "tools" / "validate_sdd.py"
    retcode_sdd, stdout_sdd, stderr_sdd = run_command_capture(
        ["uv", "run", "python", str(validate_script)], CORE_SERVICE_DIR
    )
    combined_sdd = stdout_sdd + "\n" + stderr_sdd

    if retcode_sdd != 0:
        return {
            "success": False,
            "phase": "quality",
            "error": "Quality Gate Failed: 'validate_sdd.py' failed.",
            "details": combined_sdd[-1500:],
        }

    return {
        "success": True,
        "phase": "quality",
        "message": "Quality Gate Verified: Coverage >= 90%, all Linter checks passed, and SDD requirements validated.",
    }


def main():
    parser = argparse.ArgumentParser(description="Verify SDD/TDD Loop State & Gates (JSON-First).")
    parser.add_argument(
        "--phase",
        required=True,
        choices=["outer-red", "red", "green", "quality"],
        help="Phase to verify: outer-red, green, quality",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Optional specific test file or directory path (e.g. tests/integration/test_foo.py)",
    )

    args = parser.parse_args()

    phase = "outer-red" if args.phase in ["outer-red", "red"] else args.phase

    if phase == "outer-red":
        result = verify_outer_red(args.target)
    elif phase == "green":
        result = verify_green(args.target)
    elif phase == "quality":
        result = verify_quality_gate()
    else:
        result = {"success": False, "error": f"Unknown phase: {phase}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result.get("success", False):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
