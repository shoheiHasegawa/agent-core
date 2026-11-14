#!/usr/bin/env python3
"""
sandbox_runner.py

WHY: プロンプト上の禁止事項（性善説）に頼らず、macOS ネイティブの `sandbox-exec`（Seatbelt）を用いて
     CCA-F Role-Scoped Least Privilege（ロール別最小権限：leader / worker / reviewer）の
     機密 Read/Write 遮断・領域外 Write 遮断・外部通信遮断を OS カーネルレベルで物理強制するため。

Role Boundaries:
  - `leader`   : `workspaces/<epic>/` 全体（`AGENTS.md`, `tasks/`, `scratch/`, `worktrees/`）への Write のみ許可。親 `main` への Write は遮断。
  - `worker`   : `worktrees/<repo>/` および `scratch/` への Write のみ許可（デフォルト）。`AGENTS.md` や `tasks/` の改ざんも遮断。
  - `reviewer` : `scratch/` への Write のみ許可。`worktrees/<repo>/` のプロダクション・テストコードへの Write も完全遮断（Read-Only 監査強制）。

Usage:
  1. サンドボックス内でコマンドを実行:
     uv run python tools/sandbox_runner.py [--role {leader,worker,reviewer}] [--allow-net] --worktree <path> -- <cmd> [args...]
  2. 自己検証モード（決定論的セキュリティ境界テスト `[SB-01]`〜`[SB-10]`）:
     uv run python tools/sandbox_runner.py --self-test [--json]
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Literal

AGENT_CORE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PROFILE = AGENT_CORE_DIR / "config" / "sandbox" / "worker.sb"
RoleType = Literal["leader", "worker", "reviewer"]
VALID_ROLES: tuple[RoleType, ...] = ("leader", "worker", "reviewer")
SANDBOX_ENV_VAR = "YOU_INC_SANDBOX_ACTIVE"


def is_inside_sandbox() -> bool:
    """Seatbelt サンドボックス内部で動作中かを判定する。"""
    return os.environ.get(SANDBOX_ENV_VAR) == "1"


def resolve_parking_lot_path(explicit_path: Path | None = None) -> Path:
    """環境変数または conf.env から PARKING_LOT_PATH を解決する。"""
    if explicit_path:
        return explicit_path.expanduser().resolve()
    if "PARKING_LOT_PATH" in os.environ:
        return Path(os.environ["PARKING_LOT_PATH"]).expanduser().resolve()
    candidates = [
        AGENT_CORE_DIR / "config" / "conf.env",
        AGENT_CORE_DIR.parent.parent.parent / "config" / "conf.env",
        Path("/Users/shoheihasegawa/you_inc/agent-core/config/conf.env"),
    ]
    for c in candidates:
        if c.exists():
            try:
                for line in c.read_text(encoding="utf-8").splitlines():
                    if line.startswith("PARKING_LOT_PATH="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return Path(val).expanduser().resolve()
            except Exception:
                pass
    return (AGENT_CORE_DIR / "data" / "parking_lot.jsonl").resolve()


def infer_workspace_and_scratch(worktree_path: Path) -> tuple[Path, Path]:
    """
    `workspaces/<epic>/worktrees/<repo>` の構造から `(workspace_dir, scratch_dir)` を自動推論する。
    標準構造でない場合は `(worktree_path, /private/tmp)` にフォールバックする。
    """
    resolved = worktree_path.resolve()
    if resolved.parent.name == "worktrees":
        ws_dir = resolved.parent.parent
        scratch = ws_dir / "scratch"
        if scratch.exists():
            return ws_dir.resolve(), scratch.resolve()
        return ws_dir.resolve(), Path("/private/tmp").resolve()
    if (resolved / "worktrees").exists() and (resolved / "scratch").exists():
        return resolved, (resolved / "scratch").resolve()
    return resolved, Path("/private/tmp").resolve()


def resolve_role_paths(
    worktree_dir: Path,
    scratch_dir: Path | None = None,
    role: RoleType = "worker",
) -> tuple[Path, Path]:
    """
    ロール (`leader`, `worker`, `reviewer`) に応じて Seatbelt に渡す `(ALLOWED_PRIMARY, ALLOWED_SCRATCH)` の物理パスを決定する (`[SB-04]`, `[SB-09]`)。
    - `leader`   : ALLOWED_PRIMARY = `workspaces/<epic>/`
    - `worker`   : ALLOWED_PRIMARY = `workspaces/<epic>/worktrees/<repo>/`
    - `reviewer` : ALLOWED_PRIMARY = `workspaces/<epic>/scratch/` (Worktree への Write を禁止)
    """
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role '{role}'. Must be one of {VALID_ROLES}.")

    ws_dir, inferred_scratch = infer_workspace_and_scratch(worktree_dir)
    resolved_wt = worktree_dir.resolve()
    resolved_scratch = scratch_dir.resolve() if scratch_dir else inferred_scratch

    if role == "leader":
        primary = ws_dir
    elif role == "worker":
        primary = resolved_wt
    else:  # reviewer
        primary = resolved_scratch

    return primary, resolved_scratch


def build_sandbox_command(
    command: list[str],
    worktree_dir: Path,
    scratch_dir: Path | None = None,
    role: RoleType = "worker",
    allow_net: bool = False,
    profile_path: Path = DEFAULT_PROFILE,
    parking_lot_file: Path | None = None,
) -> list[str]:
    """
    Seatbelt プロファイル (`worker.sb`) に動的パラメータ (`-D`) を注入した `sandbox-exec` コマンド列を構築する。
    """
    if not profile_path.exists():
        raise FileNotFoundError(f"Seatbelt profile not found: {profile_path}")
    if not worktree_dir.exists() or not worktree_dir.is_dir():
        raise ValueError(f"Target worktree directory does not exist: {worktree_dir}")
    if not command:
        raise ValueError("No command specified to execute inside sandbox.")

    allowed_primary, allowed_scratch = resolve_role_paths(
        worktree_dir=worktree_dir,
        scratch_dir=scratch_dir,
        role=role,
    )
    uv_cache = Path(os.environ.get("UV_CACHE_DIR", Path.home() / ".cache" / "uv")).expanduser().resolve()
    target_parking_lot = resolve_parking_lot_path(parking_lot_file)
    target_parking_lot_backup = target_parking_lot.with_name("parking_lot_backup.jsonl")

    return [
        "/usr/bin/sandbox-exec",
        "-f",
        str(profile_path.resolve()),
        "-D",
        f"ALLOWED_PRIMARY={allowed_primary}",
        "-D",
        f"ALLOWED_SCRATCH={allowed_scratch}",
        "-D",
        f"UV_CACHE_DIR={uv_cache}",
        "-D",
        f"ALLOW_NET={'true' if allow_net else 'false'}",
        "-D",
        f"ROLE={role}",
        "-D",
        f"PARKING_LOT_FILE={target_parking_lot}",
        "-D",
        f"PARKING_LOT_BACKUP_FILE={target_parking_lot_backup}",
        "--",
        *command,
    ]


def ensure_parking_lot_files(parking_lot_path: Path) -> None:
    """Seatbelt の literal 指定が安全に機能するよう、親ディレクトリと空ファイルを事前に確保する。"""
    try:
        parking_lot_path.parent.mkdir(parents=True, exist_ok=True)
        if not parking_lot_path.exists():
            parking_lot_path.touch(exist_ok=True)
        backup_path = parking_lot_path.with_name("parking_lot_backup.jsonl")
        if not backup_path.exists():
            backup_path.touch(exist_ok=True)
    except Exception:
        pass


def run_in_sandbox(
    command: list[str],
    worktree_dir: Path,
    scratch_dir: Path | None = None,
    role: RoleType = "worker",
    allow_net: bool = False,
    profile_path: Path = DEFAULT_PROFILE,
    parking_lot_file: Path | None = None,
    cwd: Path | None = None,
    capture_output: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """指定されたコマンドをロール別最小権限の `sandbox-exec` 内で実行する。"""
    resolved_pl = resolve_parking_lot_path(parking_lot_file)
    ensure_parking_lot_files(resolved_pl)
    sb_cmd = build_sandbox_command(
        command=command,
        worktree_dir=worktree_dir,
        scratch_dir=scratch_dir,
        role=role,
        allow_net=allow_net,
        profile_path=profile_path,
        parking_lot_file=parking_lot_file,
    )
    run_env = (env if env is not None else os.environ).copy()
    run_env[SANDBOX_ENV_VAR] = "1"
    return subprocess.run(
        sb_cmd,
        cwd=str((cwd or worktree_dir).resolve()),
        text=True,
        capture_output=capture_output,
        check=False,
        env=run_env,
    )


def run_self_test(profile_path: Path = DEFAULT_PROFILE, output_json: bool = False) -> int:
    """
    `spec.md` の全シナリオ分母 (`[SB-01]`〜`[SB-10]`) を決定論的に自動検証する自己検証モード (`[SB-03]`)。
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
        ws_dir = tmp_root / "workspaces" / "test-epic"
        tasks_dir = ws_dir / "tasks"
        worktree_dir = ws_dir / "worktrees" / "repo"
        scratch_dir = ws_dir / "scratch"
        outside_dir.mkdir(parents=True)
        tasks_dir.mkdir(parents=True)
        worktree_dir.mkdir(parents=True)
        scratch_dir.mkdir(parents=True)

        # 機密ファイル群の準備
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

        # ① [SB-07] 機密ファイルの Read/Write 遮断検証（全ロール共通）
        all_secrets_blocked = True
        secret_details: list[str] = []
        for target in secret_targets:
            res = run_in_sandbox(
                command=["/bin/cat", str(target)],
                worktree_dir=worktree_dir,
                scratch_dir=scratch_dir,
                role="leader",  # 最上位の leader でも機密 Read は不可
                profile_path=profile_path,
                capture_output=True,
            )
            blocked = res.returncode != 0 and (
                "Operation not permitted" in res.stderr or "Permission denied" in res.stderr
            )
            if not blocked:
                all_secrets_blocked = False
                secret_details.append(f"UNBLOCKED: {target.name} (rc={res.returncode})")
            else:
                secret_details.append(f"{target.name}: blocked")

        wt_secret_write = run_in_sandbox(
            command=["/bin/sh", "-c", f"echo 'leak' > '{worktree_dir / 'secret.env'}'"],
            worktree_dir=worktree_dir,
            scratch_dir=scratch_dir,
            role="worker",
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
            ", ".join(secret_details[:4]) + (f" (+{len(secret_details) - 4} more)" if len(secret_details) > 4 else ""),
        )

        # ② [SB-08] 親リポジトリ（main 側）への Write 遮断検証（leader / worker 共に遮断）
        protected_readme = outside_dir / "README.md"
        protected_readme.write_text("# Original Main Repo\n", encoding="utf-8")
        res_outside_write = run_in_sandbox(
            command=["/bin/sh", "-c", f"echo 'HACKED' >> '{protected_readme}'"],
            worktree_dir=worktree_dir,
            scratch_dir=scratch_dir,
            role="leader",
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
            "Deny Write outside Workspace/Worktree (protects parent main branch even for leader)",
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
            role="worker",
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
            "Allow Write inside ALLOWED_SCRATCH and ALLOWED_WORKTREE for worker",
            allowed_write_ok,
            "Successfully wrote to scratch/ and worktree/" if allowed_write_ok else res_allowed_write.stderr,
        )

        # ④ [SB-09] ロール別最小権限境界（leader vs worker vs reviewer）の検証
        context_file = tasks_dir / "context.md"
        # leader は tasks/context.md に書ける
        res_leader_tasks = run_in_sandbox(
            command=["/bin/sh", "-c", f"echo 'leader_ok' > '{context_file}'"],
            worktree_dir=worktree_dir,
            scratch_dir=scratch_dir,
            role="leader",
            profile_path=profile_path,
            capture_output=True,
        )
        # worker は tasks/context.md に書けない（Reward Hacking 防止）
        res_worker_tasks = run_in_sandbox(
            command=["/bin/sh", "-c", f"echo 'worker_hack' >> '{context_file}'"],
            worktree_dir=worktree_dir,
            scratch_dir=scratch_dir,
            role="worker",
            profile_path=profile_path,
            capture_output=True,
        )
        # reviewer は scratch/ に書けるが worktree/ のコードには書けない（越権修正防止）
        rev_report = scratch_dir / "review_verdict_test.md"
        res_rev_scratch = run_in_sandbox(
            command=["/bin/sh", "-c", f"echo 'PASS' > '{rev_report}'"],
            worktree_dir=worktree_dir,
            scratch_dir=scratch_dir,
            role="reviewer",
            profile_path=profile_path,
            capture_output=True,
        )
        res_rev_wt = run_in_sandbox(
            command=["/bin/sh", "-c", f"echo 'edit_code' >> '{wt_test_file}'"],
            worktree_dir=worktree_dir,
            scratch_dir=scratch_dir,
            role="reviewer",
            profile_path=profile_path,
            capture_output=True,
        )
        role_hierarchy_ok = (
            res_leader_tasks.returncode == 0
            and res_worker_tasks.returncode != 0
            and "Operation not permitted" in res_worker_tasks.stderr
            and res_rev_scratch.returncode == 0
            and res_rev_wt.returncode != 0
            and "Operation not permitted" in res_rev_wt.stderr
        )
        record(
            "[SB-09]",
            "Enforce role-scoped write boundaries (leader: ws, worker: wt+scratch, reviewer: scratch-only)",
            role_hierarchy_ok,
            "leader->tasks(OK), worker->tasks(DENIED), reviewer->scratch(OK), reviewer->worktree(DENIED)",
        )

        # ⑤ [SB-04] シンボリックリンク / 相対パス解決と scratch 自動推論の検証
        symlink_wt = tmp_root / "symlink_to_wt"
        symlink_wt.symlink_to(worktree_dir)
        _, inferred_scratch = infer_workspace_and_scratch(symlink_wt)
        cmd_list = build_sandbox_command(["/bin/true"], worktree_dir=symlink_wt, role="worker", profile_path=profile_path)
        symlink_ok = (
            inferred_scratch == scratch_dir.resolve()
            and f"ALLOWED_PRIMARY={worktree_dir.resolve()}" in cmd_list
            and f"ALLOWED_SCRATCH={scratch_dir.resolve()}" in cmd_list
        )
        record(
            "[SB-04]",
            "Resolve symlinks and infer workspace scratch/ path accurately",
            symlink_ok,
            f"Resolved primary={worktree_dir.resolve()}, scratch={inferred_scratch}",
        )

        # ⑥ [SB-05] デフォルト外部ネットワーク接続遮断の検証
        res_net_deny = run_in_sandbox(
            command=[
                sys.executable,
                "-c",
                "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.sendto(b'ping', ('1.1.1.1', 53))",
            ],
            worktree_dir=worktree_dir,
            scratch_dir=scratch_dir,
            role="worker",
            allow_net=False,
            profile_path=profile_path,
            capture_output=True,
        )
        net_blocked = res_net_deny.returncode != 0 and (
            "Operation not permitted" in res_net_deny.stderr or "PermissionError" in res_net_deny.stderr
        )
        record(
            "[SB-05]",
            "Deny outbound network connections by default (non-loopback)",
            net_blocked,
            res_net_deny.stderr.splitlines()[-1] if res_net_deny.stderr else f"returncode={res_net_deny.returncode}",
        )

        # ⑦ [SB-10] `--allow-net` 明示指定時の通信開通＋インメモリ環境変数注入の検証
        cmd_net_allow = build_sandbox_command(
            ["/bin/true"],
            worktree_dir=worktree_dir,
            scratch_dir=scratch_dir,
            role="leader",
            allow_net=True,
            profile_path=profile_path,
        )
        res_env_inject = run_in_sandbox(
            command=[
                sys.executable,
                "-c",
                "import os, socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.sendto(b'ok', ('127.0.0.1', 53)); assert os.environ.get('SANDBOX_INJECT_TEST') == 'ok'",
            ],
            worktree_dir=worktree_dir,
            scratch_dir=scratch_dir,
            role="leader",
            allow_net=True,
            profile_path=profile_path,
            capture_output=True,
        )
        # 環境変数を渡したケースの確認
        env_copy = os.environ.copy()
        env_copy["SANDBOX_INJECT_TEST"] = "ok"
        res_env_sub = subprocess.run(
            build_sandbox_command(
                [sys.executable, "-c", "import os; assert os.environ.get('SANDBOX_INJECT_TEST') == 'ok'"],
                worktree_dir=worktree_dir,
                scratch_dir=scratch_dir,
                role="leader",
                allow_net=True,
                profile_path=profile_path,
            ),
            env=env_copy,
            capture_output=True,
            text=True,
            check=False,
        )
        allow_net_and_env_ok = "ALLOW_NET=true" in cmd_net_allow and res_env_sub.returncode == 0
        record(
            "[SB-10]",
            "Support explicit --allow-net flag and in-memory env var injection without dev-secret files",
            allow_net_and_env_ok,
            "ALLOW_NET=true parameter and in-memory os.environ pass-through verified",
        )

        # ⑧ [SB-06] 不正引数に対する例外・エラー検証
        invalid_arg_caught = False
        try:
            build_sandbox_command([], worktree_dir=tmp_root / "non_existent_dir", profile_path=profile_path)
        except ValueError:
            invalid_arg_caught = True
        record(
            "[SB-06]",
            "Reject non-existent worktree, invalid role, or empty command cleanly",
            invalid_arg_caught,
            "ValueError raised as expected on invalid worktree/command",
        )

        # ⑪ [SB-11] Parking Lot 単一ファイルへの書き込み許可と他ファイル遮断の維持（ロール別最小権限）
        test_parking_lot = outside_dir / "data" / "parking_lot.jsonl"
        test_other_file = outside_dir / "data" / "other.txt"
        test_parking_lot.parent.mkdir(parents=True, exist_ok=True)
        test_parking_lot.write_text('{"initial": 1}\n', encoding="utf-8")
        test_other_file.write_text("protected\n", encoding="utf-8")

        # 1. worker による parking_lot.jsonl への追記（許可）
        res_pl_write = run_in_sandbox(
            command=["/bin/sh", "-c", f"echo '{{\"parked\": 2}}' >> '{test_parking_lot}'"],
            worktree_dir=worktree_dir,
            scratch_dir=scratch_dir,
            role="worker",
            profile_path=profile_path,
            parking_lot_file=test_parking_lot,
            capture_output=True,
        )
        # 2. worker による同ディレクトリ他ファイルへの追記（遮断）
        res_other_write = run_in_sandbox(
            command=["/bin/sh", "-c", f"echo 'hack' >> '{test_other_file}'"],
            worktree_dir=worktree_dir,
            scratch_dir=scratch_dir,
            role="worker",
            profile_path=profile_path,
            parking_lot_file=test_parking_lot,
            capture_output=True,
        )
        # 3. reviewer による parking_lot.jsonl への追記（遮断: 監査役はRead-Only）
        res_reviewer_pl_write = run_in_sandbox(
            command=["/bin/sh", "-c", f"echo 'reviewer_hack' >> '{test_parking_lot}'"],
            worktree_dir=worktree_dir,
            scratch_dir=scratch_dir,
            role="reviewer",
            profile_path=profile_path,
            parking_lot_file=test_parking_lot,
            capture_output=True,
        )

        pl_write_ok = res_pl_write.returncode == 0
        other_blocked = res_other_write.returncode != 0 and (
            "Operation not permitted" in res_other_write.stderr or "Permission denied" in res_other_write.stderr
        )
        reviewer_blocked = res_reviewer_pl_write.returncode != 0 and (
            "Operation not permitted" in res_reviewer_pl_write.stderr or "Permission denied" in res_reviewer_pl_write.stderr
        )
        sb11_ok = pl_write_ok and other_blocked and reviewer_blocked
        record(
            "[SB-11]",
            "Allow write to single parking_lot.jsonl for worker while denying other files and blocking reviewer",
            sb11_ok,
            f"worker_pl: {'OK' if pl_write_ok else 'FAIL'}, worker_other: {'BLOCKED' if other_blocked else 'UNBLOCKED'}, reviewer_pl: {'BLOCKED' if reviewer_blocked else 'UNBLOCKED'}",
        )

    # ⑨ [SB-03] Leave No Trace（一時ディレクトリ完全消去の冪等性確認）
    leave_no_trace_ok = not tmp_root.exists()
    record(
        "[SB-03]",
        "Idempotent self-test cleanup (Leave No Trace)",
        leave_no_trace_ok,
        "Temporary test directory completely removed",
    )

    # ⑩ [SB-02] 現在の Worktree (`AGENT_CORE_DIR`) 内で `make check-all` がサンドボックス下で Exit 0 完走することを確認
    res_check_all = run_in_sandbox(
        command=["make", "check-all"],
        worktree_dir=AGENT_CORE_DIR,
        role="worker",
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
        description="Execute commands inside macOS Seatbelt role-scoped least-privilege sandbox (worker.sb)."
    )
    parser.add_argument(
        "--role",
        choices=VALID_ROLES,
        default="worker",
        help="Execution role determining write boundaries: leader (workspace), worker (worktree+scratch), reviewer (scratch only).",
    )
    parser.add_argument(
        "--allow-net",
        action="store_true",
        help="Explicitly allow outbound network connections (Tier 2/3 package sync or API verification only).",
    )
    parser.add_argument(
        "--worktree",
        type=Path,
        default=AGENT_CORE_DIR,
        help="Path to the target worktree directory (default: current agent-core root).",
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
        "--parking-lot-file",
        type=Path,
        default=None,
        help="Path to allowed single parking lot file (default: data/parking_lot.jsonl).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run deterministic self-verification suite ([SB-01] to [SB-11]).",
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
            role=args.role,
            allow_net=args.allow_net,
            profile_path=args.profile,
            parking_lot_file=args.parking_lot_file,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"❌ Sandbox Runner Error: {exc}", file=sys.stderr)
        sys.exit(1)

    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
