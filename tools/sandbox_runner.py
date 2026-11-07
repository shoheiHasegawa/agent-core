#!/usr/bin/env python3
"""
sandbox_runner.py

WHY: プロンプト上の禁止事項（性善説）に頼らず、macOS ネイティブの `sandbox-exec`（Seatbelt）を用いて
     ワーカー実行時の最小権限（機密 Read/Write 遮断・Worktree 外 Write 遮断・外部通信遮断）を物理強制するため。

Usage:
  1. サンドボックス内でコマンドを実行:
     uv run python tools/sandbox_runner.py --worktree <path> [--scratch <path>] -- <cmd> [args...]
  2. 自己検証モード（決定論的セキュリティ境界テスト `[SB-01]`〜`[SB-08]`）:
     uv run python tools/sandbox_runner.py --self-test [--json]
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

AGENT_CORE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PROFILE = AGENT_CORE_DIR / "config" / "sandbox" / "worker.sb"


def infer_scratch_dir(worktree_path: Path) -> Path:
    """
    `workspaces/<epic>/worktrees/<repo>` の構造から `workspaces/<epic>/scratch` を自動推論する。
    該当しない場合は `/private/tmp` にフォールバックする。
    """
    resolved = worktree_path.resolve()
    if resolved.parent.name == "worktrees":
        candidate = resolved.parent.parent / "scratch"
        if candidate.exists():
            return candidate.resolve()
    return Path("/private/tmp").resolve()


def build_sandbox_command(
    command: list[str],
    worktree_dir: Path,
    scratch_dir: Path | None = None,
    profile_path: Path = DEFAULT_PROFILE,
) -> list[str]:
    """
    Seatbelt プロファイル (`worker.sb`) に動的パラメータ (`-D`) を注入した `sandbox-exec` コマンド列を構築する (`[SB-04]`)。
    macOS の `/tmp` -> `/private/tmp` 等のシンボリックリンクによる subpath 不一致を防ぐため、すべて `resolve()` で物理パス化する。
    """
    if not profile_path.exists():
        raise FileNotFoundError(f"Seatbelt profile not found: {profile_path}")
    if not worktree_dir.exists() or not worktree_dir.is_dir():
        raise ValueError(f"Target worktree directory does not exist: {worktree_dir}")
    if not command:
        raise ValueError("No command specified to execute inside sandbox.")

    resolved_wt = worktree_dir.resolve()
    resolved_scratch = (scratch_dir or infer_scratch_dir(resolved_wt)).resolve()
    uv_cache = Path(os.environ.get("UV_CACHE_DIR", Path.home() / ".cache" / "uv")).expanduser().resolve()

    return [
        "/usr/bin/sandbox-exec",
        "-f",
        str(profile_path.resolve()),
        "-D",
        f"ALLOWED_WORKTREE={resolved_wt}",
        "-D",
        f"ALLOWED_SCRATCH={resolved_scratch}",
        "-D",
        f"UV_CACHE_DIR={uv_cache}",
        "--",
        *command,
    ]


def run_in_sandbox(
    command: list[str],
    worktree_dir: Path,
    scratch_dir: Path | None = None,
    profile_path: Path = DEFAULT_PROFILE,
    cwd: Path | None = None,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    """指定されたコマンドを `sandbox-exec` 内で実行する。"""
    sb_cmd = build_sandbox_command(
        command=command,
        worktree_dir=worktree_dir,
        scratch_dir=scratch_dir,
        profile_path=profile_path,
    )
    return subprocess.run(
        sb_cmd,
        cwd=str((cwd or worktree_dir).resolve()),
        text=True,
        capture_output=capture_output,
        check=False,
    )


def run_self_test(profile_path: Path = DEFAULT_PROFILE, output_json: bool = False) -> int:
    """
    `spec.md` の全シナリオ分母 (`[SB-01]`〜`[SB-08]`) を決定論的に自動検証する自己検証モード (`[SB-03]`)。
    1. `[SB-07]` 機密ファイル (`config/secret.env`, `*.pem`, `*.key`, `token.json`, `credentials.json`, `client_secret.json`) の Read/Write 拒否
    2. `[SB-08]` Worktree 外（親ディレクトリ・保護領域）への Write 拒否
    3. `[SB-01]` 許可された `scratch/` および `worktree/` への Write 成功
    4. `[SB-04]` シンボリックリンク / 相対パスの物理パス正規化解決
    5. `[SB-05]` 外部ネットワーク通信の遮断
    6. `[SB-06]` 不正引数に対する安全なエラーハンドリング
    7. `[SB-02]` サンドボックス内での対象 Worktree `make check-all` の Exit 0 完走
    """
    checks: list[dict[str, Any]] = []

    def record(scenario_id: str, name: str, passed: bool, detail: str) -> None:
        checks.append(
            {
                "scenario": scenario_id,
                "name": name,
                "status": "PASS" if passed else "FAIL",
                "detail": detail.strip(),
            }
        )

    with tempfile.TemporaryDirectory(prefix="you_inc_sb_selftest_") as tmp_root_str:
        tmp_root = Path(tmp_root_str).resolve()
        outside_dir = tmp_root / "outside_main_repo"
        worktree_dir = tmp_root / "workspaces" / "test-epic" / "worktrees" / "repo"
        scratch_dir = tmp_root / "workspaces" / "test-epic" / "scratch"
        outside_dir.mkdir(parents=True)
        worktree_dir.mkdir(parents=True)
        scratch_dir.mkdir(parents=True)

        # 親の agent-core/config/secret.env が実在すればそれも検証対象に含めつつ、
        # 環境非依存で全機密パターンを検証できるよう outside_dir と worktree_dir にもダミー機密ファイルを配置する
        secret_filenames = [
            "secret.env",
            "dummy.pem",
            "dummy.key",
            "token.json",
            "credentials.json",
            "client_secret.json",
        ]
        secret_targets: list[Path] = []
        for fname in secret_filenames:
            f_path = outside_dir / fname
            f_path.write_text("TOP_SECRET_DATA\n", encoding="utf-8")
            secret_targets.append(f_path)

        # 実在する config/secret.env の検証（存在しない場合は worktree 内 config/secret.env の一時ダミーで検証）
        real_secret_env = AGENT_CORE_DIR / "config" / "secret.env"
        parent_secret_env = AGENT_CORE_DIR.parent.parent.parent / "config" / "secret.env"
        if real_secret_env.exists():
            secret_targets.insert(0, real_secret_env)
        elif parent_secret_env.exists():
            secret_targets.insert(0, parent_secret_env)
        else:
            wt_config_secret = worktree_dir / "config" / "secret.env"
            wt_config_secret.parent.mkdir(parents=True, exist_ok=True)
            wt_config_secret.write_text("DUMMY_SECRET_ENV=1\n", encoding="utf-8")
            secret_targets.insert(0, wt_config_secret)

        # ① [SB-07] 機密ファイルの Read 遮断検証 (`Operation not permitted`)
        all_secrets_blocked = True
        secret_details: list[str] = []
        for target in secret_targets:
            res = run_in_sandbox(
                command=["/bin/cat", str(target)],
                worktree_dir=worktree_dir,
                scratch_dir=scratch_dir,
                profile_path=profile_path,
                capture_output=True,
            )
            blocked = res.returncode != 0 and (
                "Operation not permitted" in res.stderr or "Permission denied" in res.stderr
            )
            if not blocked:
                all_secrets_blocked = False
                secret_details.append(f"UNBLOCKED: {target.name} (rc={res.returncode}, stderr={res.stderr})")
            else:
                secret_details.append(f"{target.name}: blocked ({res.stderr.strip()})")

        # Worktree 内であっても secret.env への新規書き込みが拒否されることを確認
        wt_secret_write = run_in_sandbox(
            command=["/bin/sh", "-c", f"echo 'leak' > '{worktree_dir / 'secret.env'}'"],
            worktree_dir=worktree_dir,
            scratch_dir=scratch_dir,
            profile_path=profile_path,
            capture_output=True,
        )
        if wt_secret_write.returncode == 0:
            all_secrets_blocked = False
            secret_details.append("UNBLOCKED write to secret.env inside worktree")

        record(
            "[SB-07]",
            "Deny Read/Write on secret.env, *.pem, *.key, token.json, credentials.json, client_secret.json",
            all_secrets_blocked,
            "; ".join(secret_details[:3]) + (f" (+{len(secret_details) - 3} more)" if len(secret_details) > 3 else ""),
        )

        # ② [SB-08] Worktree 外（親リポジトリの main 側）への Write 遮断検証
        protected_readme = outside_dir / "README.md"
        protected_readme.write_text("# Original Main Repo\n", encoding="utf-8")
        res_outside_write = run_in_sandbox(
            command=["/bin/sh", "-c", f"echo 'HACKED' >> '{protected_readme}'"],
            worktree_dir=worktree_dir,
            scratch_dir=scratch_dir,
            profile_path=profile_path,
            capture_output=True,
        )
        outside_write_blocked = (
            res_outside_write.returncode != 0
            and "Operation not permitted" in res_outside_write.stderr
            and protected_readme.read_text(encoding="utf-8") == "# Original Main Repo\n"
        )
        record(
            "[SB-08]",
            "Deny Write outside ALLOWED_WORKTREE and ALLOWED_SCRATCH",
            outside_write_blocked,
            res_outside_write.stderr or f"returncode={res_outside_write.returncode}",
        )

        # ③ [SB-01] 許可された `scratch/` および `worktree/` への書き込み成功検証
        scratch_test_file = scratch_dir / "sandbox_write_ok.txt"
        wt_test_file = worktree_dir / "wt_write_ok.txt"
        res_allowed_write = run_in_sandbox(
            command=[
                "/bin/sh",
                "-c",
                f"echo 'scratch_ok' > '{scratch_test_file}' && echo 'wt_ok' > '{wt_test_file}'",
            ],
            worktree_dir=worktree_dir,
            scratch_dir=scratch_dir,
            profile_path=profile_path,
            capture_output=True,
        )
        allowed_write_ok = (
            res_allowed_write.returncode == 0
            and scratch_test_file.exists()
            and scratch_test_file.read_text(encoding="utf-8").strip() == "scratch_ok"
            and wt_test_file.exists()
        )
        record(
            "[SB-01]",
            "Allow Write inside ALLOWED_SCRATCH and ALLOWED_WORKTREE",
            allowed_write_ok,
            "Successfully wrote to scratch/ and worktree/" if allowed_write_ok else res_allowed_write.stderr,
        )

        # ④ [SB-04] シンボリックリンク / 相対パス解決と scratch 自動推論の検証
        symlink_wt = tmp_root / "symlink_to_wt"
        symlink_wt.symlink_to(worktree_dir)
        inferred_scratch = infer_scratch_dir(symlink_wt)
        cmd_list = build_sandbox_command(["/bin/true"], worktree_dir=symlink_wt, profile_path=profile_path)
        symlink_ok = (
            inferred_scratch == scratch_dir.resolve()
            and f"ALLOWED_WORKTREE={worktree_dir.resolve()}" in cmd_list
            and f"ALLOWED_SCRATCH={scratch_dir.resolve()}" in cmd_list
        )
        record(
            "[SB-04]",
            "Resolve symlinks and infer workspace scratch/ path accurately",
            symlink_ok,
            f"Resolved worktree={worktree_dir.resolve()}, scratch={inferred_scratch}",
        )

        # ⑤ [SB-05] 外部ネットワーク接続遮断の検証（外部環境非依存で即座にカーネル判定される UDP sendto を使用）
        res_net = run_in_sandbox(
            command=[
                sys.executable,
                "-c",
                "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.sendto(b'ping', ('1.1.1.1', 53))",
            ],
            worktree_dir=worktree_dir,
            scratch_dir=scratch_dir,
            profile_path=profile_path,
            capture_output=True,
        )
        net_blocked = res_net.returncode != 0 and (
            "Operation not permitted" in res_net.stderr or "PermissionError" in res_net.stderr
        )
        record(
            "[SB-05]",
            "Deny outbound network connections (non-loopback)",
            net_blocked,
            res_net.stderr.splitlines()[-1] if res_net.stderr else f"returncode={res_net.returncode}",
        )

        # ⑥ [SB-06] 不正引数に対する例外・エラー検証
        invalid_arg_caught = False
        try:
            build_sandbox_command([], worktree_dir=tmp_root / "non_existent_dir", profile_path=profile_path)
        except ValueError:
            invalid_arg_caught = True
        record(
            "[SB-06]",
            "Reject non-existent worktree or empty command cleanly",
            invalid_arg_caught,
            "ValueError raised as expected on invalid worktree/command",
        )

    # ⑦ [SB-03] Leave No Trace（一時ディレクトリ完全消去の冪等性確認）
    leave_no_trace_ok = not tmp_root.exists()
    record(
        "[SB-03]",
        "Idempotent self-test cleanup (Leave No Trace)",
        leave_no_trace_ok,
        "Temporary test directory completely removed",
    )

    # ⑧ [SB-02] 現在の Worktree (`AGENT_CORE_DIR`) 内で `make check-all` がサンドボックス下で Exit 0 完走することを確認
    res_check_all = run_in_sandbox(
        command=["make", "check-all"],
        worktree_dir=AGENT_CORE_DIR,
        profile_path=profile_path,
        cwd=AGENT_CORE_DIR,
        capture_output=True,
    )
    check_all_ok = res_check_all.returncode == 0
    record(
        "[SB-02]",
        "Run 'make check-all' inside sandbox on current agent-core worktree",
        check_all_ok,
        "make check-all exited with 0" if check_all_ok else (res_check_all.stderr or res_check_all.stdout),
    )

    all_passed = all(c["status"] == "PASS" for c in checks)
    summary = {
        "status": "PASS" if all_passed else "FAIL",
        "total": len(checks),
        "passed": sum(1 for c in checks if c["status"] == "PASS"),
        "failed": sum(1 for c in checks if c["status"] == "FAIL"),
        "checks": checks,
    }

    if output_json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print("====================================================")
        print(" 🛡️  Sandbox Runner Self-Test (Seatbelt Verification)")
        print("====================================================")
        for c in checks:
            icon = "✅" if c["status"] == "PASS" else "❌"
            print(f" {icon} {c['scenario']} {c['name']}")
            print(f"    └─ {c['detail']}")
        print("----------------------------------------------------")
        if all_passed:
            print(f"🎉 Result: PASS ({summary['passed']}/{summary['total']} scenarios verified)")
        else:
            print(f"❌ Result: FAIL ({summary['failed']} scenario(s) failed)")

    return 0 if all_passed else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Execute commands inside macOS Seatbelt least-privilege sandbox (worker.sb)."
    )
    parser.add_argument(
        "--worktree",
        type=Path,
        default=AGENT_CORE_DIR,
        help="Path to the allowed worktree directory (default: current agent-core root).",
    )
    parser.add_argument(
        "--scratch",
        type=Path,
        default=None,
        help="Path to the allowed scratch directory (default: inferred from workspace or /private/tmp).",
    )
    parser.add_argument(
        "--profile",
        type=Path,
        default=DEFAULT_PROFILE,
        help="Path to the Seatbelt .sb profile (default: config/sandbox/worker.sb).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run deterministic self-verification suite ([SB-01] to [SB-08]).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output self-test results in JSON format.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command and arguments to execute inside sandbox (prefix with '--').",
    )

    args = parser.parse_args()

    if args.self_test:
        sys.exit(run_self_test(profile_path=args.profile, output_json=args.json))

    cmd = list(args.command)
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]

    if not cmd:
        parser.error("No command specified. Use '-- <command> [args...]' or '--self-test'.")

    try:
        res = run_in_sandbox(
            command=cmd,
            worktree_dir=args.worktree,
            scratch_dir=args.scratch,
            profile_path=args.profile,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"❌ Sandbox Runner Error: {exc}", file=sys.stderr)
        sys.exit(1)

    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
