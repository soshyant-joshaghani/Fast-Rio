"""fast-rio-ctrl prod — local compose.yml helpers (Docker Desktop smoke / on-box)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from lib.config import ROOT

REMOTE = ROOT / "remote"

# CLI action → script stem under __ctrl__/remote/
ACTIONS: dict[str, str] = {
    "start": "start-prod",
    "stop": "stop-prod",
    "reset": "reset-prod",
    "backup-acme": "backup-acme",
    "restore-acme": "restore-acme",
    "prune-build": "prune-docker-build",
    "migrate-acme": "migrate-letsencrypt-from-volume",
    "setup-ubuntu": "setup-ubuntu",
}


def _run_remote_script(stem: str, extra: list[str] | None = None) -> int:
    extra = list(extra or [])
    if sys.platform == "win32":
        if stem == "setup-ubuntu":
            print(
                "error: setup-ubuntu is a Linux VM script.\n"
                "  On the VM:  bash __ctrl__/remote/setup-ubuntu.sh\n"
                "  From laptop: fast-rio-ctrl.bat setup",
                file=sys.stderr,
            )
            return 1
        script = REMOTE / f"{stem}.bat"
        if not script.is_file():
            print(f"error: missing {script}", file=sys.stderr)
            return 1
        cmd = ["cmd", "/c", str(script), *extra]
    else:
        script = REMOTE / f"{stem}.sh"
        if not script.is_file():
            print(f"error: missing {script}", file=sys.stderr)
            return 1
        cmd = ["bash", str(script), *extra]

    print(f"[fast-rio] {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=ROOT).returncode


def cmd_prod(args: argparse.Namespace) -> int:
    action = args.prod_action
    stem = ACTIONS.get(action)
    if not stem:
        print(f"error: unknown prod action {action!r}", file=sys.stderr)
        return 1
    extra: list[str] = []
    if action == "migrate-acme" and getattr(args, "volume", None):
        extra.append(args.volume)
    return _run_remote_script(stem, extra)


def _prod_help(args: argparse.Namespace) -> int:
    _ = args
    print(
        "usage: fast-rio-ctrl.bat prod {start,stop,reset,backup-acme,restore-acme,"
        "prune-build,migrate-acme,setup-ubuntu}\n"
        "\n"
        "Runs __ctrl__/remote/* against local compose.yml (Docker Desktop smoke test\n"
        "or when you are already on the VM). For remote SSH deploy use:\n"
        "  start / stop / update / backup-acme  (no 'prod' prefix)\n"
        "\n"
        "examples:\n"
        "  fast-rio-ctrl.bat prod start\n"
        "  fast-rio-ctrl.bat prod stop\n"
        "  fast-rio-ctrl.bat prod reset\n"
        "  fast-rio-ctrl.bat prod backup-acme\n"
    )
    return 0


def build_prod_subparser(sub: argparse._SubParsersAction) -> None:
    sp = sub.add_parser(
        "prod",
        help="Local production compose helpers (see also SSH start/stop)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  fast-rio-ctrl.bat prod start\n"
            "  fast-rio-ctrl.bat prod stop\n"
            "  fast-rio-ctrl.bat prod reset\n"
            "  fast-rio-ctrl.bat prod backup-acme\n"
            "\n"
            "SSH deploy (no prod prefix): start | stop | update | backup-acme"
        ),
    )
    sp.set_defaults(func=_prod_help)
    actions = sp.add_subparsers(dest="prod_action", required=False)

    for name, help_ in [
        ("start", "compose up -d --build (local)"),
        ("stop", "compose down - keep volumes + SSL"),
        ("reset", "Wipe DB/Redis volumes + app images; keep SSL"),
        ("backup-acme", "Copy acme.json to parent .foxg-ssl-backups"),
        ("restore-acme", "Restore acme.json from parent backup"),
        ("prune-build", "Backup SSL then docker builder prune -af"),
        ("migrate-acme", "Copy acme.json from legacy Docker volume"),
        ("setup-ubuntu", "One-time Ubuntu VM bootstrap (Linux only)"),
    ]:
        action_sp = actions.add_parser(name, help=help_)
        if name == "migrate-acme":
            action_sp.add_argument(
                "volume",
                nargs="?",
                default=None,
                help="legacy volume name (optional)",
            )
        action_sp.set_defaults(func=cmd_prod, prod_action=name)
