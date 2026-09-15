"""fast-rio-ctrl test — run pytest suites (backend / frontend)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from lib.config import ROOT
from utils.dev.cli import _setup_local, _venv_python

PROJECT = ROOT.parent


def _coverage_exe(py: Path) -> list[str]:
    return [str(py), "-m", "coverage"]


def _run_backend() -> int:
    py = _venv_python()
    if not py:
        print("error: missing project .venv — run: fast-rio-ctrl setup-local", file=sys.stderr)
        return 1

    backend = PROJECT / "backend"
    tests_backend = PROJECT / "tests" / "backend"
    env = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join([str(backend), str(tests_backend)]),
    }
    cov = _coverage_exe(py)

    print("[fast-rio] Backend tests (pytest + coverage)")
    print("  Requires dev DB: fast-rio-ctrl.bat dev run infra  (localhost:5432)")
    steps: list[list[str]] = [
        [str(py), "app/tests_pre_start.py"],
        [*cov, "run", "-m", "pytest", str(tests_backend)],
        [*cov, "report"],
    ]
    for cmd in steps:
        print(f"  {' '.join(cmd)}")
        proc = subprocess.run(cmd, cwd=backend, env=env)
        if proc.returncode != 0:
            print("Backend tests failed.", file=sys.stderr)
            return proc.returncode
    print("Backend tests passed.")
    return 0


def _run_frontend() -> int:
    py = _venv_python()
    if not py:
        print("error: missing project .venv — run: fast-rio-ctrl setup-local", file=sys.stderr)
        return 1

    env = {
        **os.environ,
        "PYTHONPATH": str(PROJECT / "frontend"),
    }
    cmd = [str(py), "-m", "pytest", str(PROJECT / "tests" / "frontend"), "-v"]
    print("[fast-rio] Frontend tests (pytest)")
    print(f"  {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=PROJECT, env=env)
    if proc.returncode != 0:
        print("Frontend tests failed.", file=sys.stderr)
        return proc.returncode
    print("Frontend tests passed.")
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    code = _setup_local(force_install=False)
    if code != 0:
        return code

    target = args.target
    if target in ("backend", "all"):
        code = _run_backend()
        if code != 0:
            return code
    if target in ("frontend", "all"):
        code = _run_frontend()
        if code != 0:
            return code
    if target == "all":
        print("\nAll tests passed.")
    return 0


def _test_help(args: argparse.Namespace) -> int:
    _ = args
    print(
        "usage: fast-rio-ctrl.bat test {all,backend,frontend}\n"
        "\n"
        "examples:\n"
        "  fast-rio-ctrl.bat test all\n"
        "  fast-rio-ctrl.bat test backend\n"
        "  fast-rio-ctrl.bat test frontend\n"
        "\n"
        "Backend needs the dev DB (fast-rio-ctrl.bat dev run infra)."
    )
    return 0


def build_test_subparser(sub: argparse._SubParsersAction) -> None:
    sp = sub.add_parser(
        "test",
        help="Run pytest suites (backend / frontend)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  fast-rio-ctrl.bat test all\n"
            "  fast-rio-ctrl.bat test backend\n"
            "  fast-rio-ctrl.bat test frontend"
        ),
    )
    sp.set_defaults(func=_test_help)
    actions = sp.add_subparsers(dest="test_target", required=False)

    for name, help_ in [
        ("all", "Backend then frontend"),
        ("backend", "pytest + coverage under tests/backend"),
        ("frontend", "pytest under tests/frontend"),
    ]:
        action_sp = actions.add_parser(name, help=help_)
        action_sp.set_defaults(func=cmd_test, target=name)
