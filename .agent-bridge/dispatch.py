#!/usr/bin/env python3
"""Restricted command dispatcher for the MineOS Codespace Actions runner.

Only the allow-listed operations below are executable. This intentionally
does not accept arbitrary shell commands from request.json.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
ALLOWED_OPERATIONS = {"diagnostics", "tests", "browser_use_install", "browser_use_doctor"}


def run(command: list[str], *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> int:
    print("$ " + " ".join(command), flush=True)
    result = subprocess.run(command, cwd=cwd, env=env, check=False)
    return result.returncode


def diagnostics() -> int:
    print("=== MINEOS CODESPACE RUNNER DIAGNOSTICS ===", flush=True)
    print(f"workspace: {ROOT}", flush=True)

    checks = [
        (["git", "branch", "--show-current"], ROOT),
        (["git", "log", "-1", "--oneline"], ROOT),
        (["git", "status", "--short", "--branch"], ROOT),
        ([sys.executable, "--version"], ROOT),
    ]
    for command, cwd in checks:
        code = run(command, cwd=cwd)
        if code:
            return code

    uv = shutil.which("uv")
    print(f"uv: {uv or 'not installed'}", flush=True)
    if uv:
        code = run([uv, "--version"])
        if code:
            return code

    browser_use = shutil.which("browser-use")
    print(f"browser-use: {browser_use or 'not installed'}", flush=True)
    if browser_use:
        code = run([browser_use, "--version"])
        if code:
            print("browser-use --version returned a non-zero exit code", flush=True)

    sshd = shutil.which("sshd")
    print(f"sshd: {sshd or 'not installed'}", flush=True)
    return 0


def tests() -> int:
    uv = shutil.which("uv")
    if not uv:
        print("uv is required for the reproducible Python 3.12 test environment", file=sys.stderr)
        return 127
    project = ROOT / "research" / "fixed-plant-bearing-baseline"
    env = dict(__import__("os").environ)
    env["UV_HTTP_TIMEOUT"] = "180"
    env["UV_HTTP_RETRIES"] = "10"
    return run(
        [uv, "run", "--python", "3.12", "--project", str(project), "--extra", "test", "pytest", "-ra"],
        cwd=ROOT,
        env=env,
    )


def browser_use_install() -> int:
    uv = shutil.which("uv")
    if not uv:
        print("uv is required to install Browser Use", file=sys.stderr)
        return 127
    env = dict(__import__("os").environ)
    env["UV_HTTP_CONNECT_TIMEOUT"] = "60"
    env["UV_HTTP_TIMEOUT"] = "180"
    env["UV_HTTP_RETRIES"] = "10"
    return run([uv, "tool", "install", "--python", "3.12", "--upgrade", "browser-use"], env=env)


def browser_use_doctor() -> int:
    executable = shutil.which("browser-use")
    if not executable:
        print("browser-use is not installed", file=sys.stderr)
        return 127
    return run([executable, "--doctor"])


HANDLERS = {
    "diagnostics": diagnostics,
    "tests": tests,
    "browser_use_install": browser_use_install,
    "browser_use_doctor": browser_use_doctor,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True, type=Path)
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))

    if not isinstance(request, dict):
        raise SystemExit("request must be a JSON object")
    if set(request) - {"request_id", "operation"}:
        raise SystemExit("request contains unsupported fields")
    request_id = request.get("request_id")
    operation = request.get("operation")
    if not isinstance(request_id, str) or not REQUEST_ID_RE.fullmatch(request_id):
        raise SystemExit("request_id must be 1-80 letters, digits, dots, underscores or hyphens")
    if operation not in ALLOWED_OPERATIONS:
        raise SystemExit(f"unsupported operation: {operation!r}")

    print(f"request_id: {request_id}", flush=True)
    print(f"operation: {operation}", flush=True)
    return HANDLERS[operation]()


if __name__ == "__main__":
    raise SystemExit(main())
