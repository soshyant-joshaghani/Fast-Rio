#!/usr/bin/env python3
"""<kit>-ctrl seed — demo data via the public Admin/user APIs (no raw SQL)."""

from __future__ import annotations

import argparse
import os
import sys
import urllib.parse
from pathlib import Path

_CTRL = Path(__file__).resolve().parents[2]
if str(_CTRL) not in sys.path:
    sys.path.insert(0, str(_CTRL))

from utils.seed.common.api_client import ApiClient
from utils.seed.common.auth import AuthSession, load_env_file, login
from utils.seed.common.paths import CTRL_NAME, CTRL_ROOT, SEED_ROOT

DEFAULT_API = "http://api.localhost"


def _packs() -> list[str]:
    """Seed targets in dependency order; a pack exists only if the kit ships its module."""
    return [
        name
        for name in ("users", "notes", "vendors")
        if (SEED_ROOT / name / f"seed_{name}.py").is_file()
    ]


def _epilog() -> str:
    targets = _packs()
    return f"""
targets:
  {', '.join(targets)}, all   (all = {' -> '.join(targets)})

examples (dev):
  {CTRL_NAME} seed all --api {DEFAULT_API}
  {CTRL_NAME} seed users --env ..\\.env
  {CTRL_NAME} seed all --purge

flags:
  --api           API base URL. Local default: {DEFAULT_API}
  --env           .env with FIRST_SUPERUSER + FIRST_SUPERUSER_PASSWORD
  --purge         Delete rows this seed created (tracked in .state/), then stop
  --allow-remote  Required for any non-local API (seed users have known passwords)

data:
  utils/seed/<target>/*.json   seed packs
  utils/seed/.state/           seed-key -> remote UUID maps (gitignored)
"""


def _default_env_path() -> Path:
    return CTRL_ROOT.parent / ".env"


def _is_local(api: str) -> bool:
    host = (urllib.parse.urlsplit(api).hostname or "").lower()
    return (
        host == "localhost"
        or host.endswith(".localhost")
        or host in {"127.0.0.1", "::1"}
    )


def _normalize_api(api: str | None) -> str:
    raw = (api or DEFAULT_API).strip().rstrip("/")
    if not raw:
        return DEFAULT_API
    if "://" not in raw:
        host = raw.lower()
        if "localhost" in host or host.startswith("127.0.0.1"):
            raw = f"http://{raw}"
        else:
            raw = f"https://{raw}"
    parsed = urllib.parse.urlsplit(raw)
    # Plain http to a real host trips Traefik's 308 and urllib drops the POST body.
    if parsed.scheme == "http" and not _is_local(raw):
        raw = urllib.parse.urlunsplit(
            ("https", parsed.netloc, parsed.path, parsed.query, parsed.fragment)
        )
    return raw.rstrip("/")


def _super_login(api: str, env_path: Path) -> AuthSession:
    env = load_env_file(env_path)
    email = env.get("FIRST_SUPERUSER")
    password = env.get("FIRST_SUPERUSER_PASSWORD")
    if not email or not password:
        raise SystemExit(
            f"FIRST_SUPERUSER / FIRST_SUPERUSER_PASSWORD missing in {env_path}"
        )
    print(f"login SuperAdmin {email} @ {api}")
    return login(ApiClient(api), email, password)


def _run_pack(name: str, session: AuthSession, *, purge: bool, api: str) -> None:
    if name == "users":
        from utils.seed.users.seed_users import seed_users

        seed_users(session, purge=purge, api_base=api)
    elif name == "notes":
        from utils.seed.notes.seed_notes import seed_notes

        seed_notes(session, purge=purge, api_base=api)
    elif name == "vendors":
        from utils.seed.vendors.seed_vendors import seed_vendors

        seed_vendors(session, purge=purge, api_base=api)
    else:  # pragma: no cover - guarded by argparse choices
        raise SystemExit(f"unknown seed target {name!r}")


def run_seed(args: argparse.Namespace) -> int:
    target = args.target
    api = _normalize_api(args.api)
    env_path = Path(args.env) if args.env else _default_env_path()
    purge = bool(args.purge)

    if not _is_local(api) and not args.allow_remote:
        raise SystemExit(
            f"refusing to seed non-local API {api}: demo users have known passwords. "
            "Re-run with --allow-remote if that is really intended."
        )

    packs = _packs()
    selected = packs if target == "all" else [target]
    if purge:
        selected = list(reversed(selected))  # children before parents

    print(f"seed target={target} api={api} env={env_path}{' PURGE' if purge else ''}")
    # Seed packs read MinIO/other settings from the environment when they need them.
    for key, value in load_env_file(env_path).items():
        os.environ.setdefault(key, value)
    session = _super_login(api, env_path)

    for name in selected:
        print(f"[{name}]")
        _run_pack(name, session, purge=purge, api=api)
    print("seed done")
    return 0


def _seed_help(_: argparse.Namespace) -> int:
    targets = _packs()
    print(
        f"usage: {CTRL_NAME}.bat seed <{'|'.join(targets + ['all'])}> [options]\n"
        "\n"
        "Seed demo data through the public APIs. Safe to re-run (idempotent).\n"
        "\n"
        "examples:\n"
        f"  {CTRL_NAME}.bat seed all --api {DEFAULT_API}\n"
        f"  {CTRL_NAME}.bat seed users\n"
        "\n"
        "options:\n"
        f"  --api URL        API base (default {DEFAULT_API})\n"
        "  --env PATH       SuperAdmin .env (default: ../.env)\n"
        "  --purge          Remove rows this seed created (tracked in .state/)\n"
        "  --allow-remote   Permit a non-local API\n"
        "\n"
        f"See also: {SEED_ROOT / 'README.md'}"
    )
    return 0


def build_seed_subparser(sub: argparse._SubParsersAction) -> None:
    sp = sub.add_parser(
        "seed",
        help="Seed demo data via the API (users, notes, ...)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Upsert demo data through the public Admin/user APIs.\n"
            "No direct DB writes. Auth: FIRST_SUPERUSER from --env."
        ),
        epilog=_epilog(),
    )
    sp.set_defaults(func=_seed_help)

    actions = sp.add_subparsers(dest="target", required=False)
    for name in [*_packs(), "all"]:
        tp = actions.add_parser(
            name,
            help="Upsert every pack" if name == "all" else f"Upsert the {name} pack",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=_epilog(),
        )
        tp.add_argument("--api", default=DEFAULT_API, help=f"API base URL (default {DEFAULT_API})")
        tp.add_argument("--env", default=None, help="path to .env with FIRST_SUPERUSER (default: ../.env)")
        tp.add_argument("--purge", action="store_true", help="delete rows this seed created")
        tp.add_argument("--allow-remote", action="store_true", help="permit a non-local API")
        tp.set_defaults(func=run_seed, target=name)
