# Seed packs

Seeds demo data through the **public APIs** (no raw SQL), so it works against any backend that follows the [FoxG wire contract](../../../../../../CONTRACT.md). Fresh databases are **not** auto-seeded; the CLI is the source of truth. Re-running is safe: rows are matched first and only missing ones are created.

## Commands

```bat
__ctrl__\fast-rio-ctrl.bat seed all --api http://api.localhost
__ctrl__\fast-rio-ctrl.bat seed users --env ..\.env
__ctrl__\fast-rio-ctrl.bat seed notes
__ctrl__\fast-rio-ctrl.bat seed all --purge
```

| Flag | Meaning |
|------|---------|
| `--api URL` | API base. Default `http://api.localhost` |
| `--env PATH` | `.env` holding `FIRST_SUPERUSER` / `FIRST_SUPERUSER_PASSWORD` (default `../.env`) |
| `--purge` | Delete the rows this seed created (tracked in `.state/`), children first, then stop |
| `--allow-remote` | Required for any non-local API. The demo users have **known passwords**, so never seed production |

Run after infra + API are up (`dev run all` or `dev run all --slim`).

## Packs

| Pack | Source | Notes |
|------|--------|-------|
| `users` | `users/users.json` | Demo users via `POST /base/users/admin`; existing emails are left untouched |
| `notes` | `notes/notes.json` | Sample notes; each is created **as its owner** (notes are owner-scoped), matched by owner + title |

`all` runs the packs in dependency order (listed above).

Demo credentials live in `users/users.json` (dev only). Add a pack by dropping `utils/seed/<name>/seed_<name>.py` and `<name>.json`, then registering it in `cli.py`.

## State

`.state/<pack>.<api-host>.json` maps seed keys to remote UUIDs so `--purge` knows what it owns. It is scoped per API host (so local and remote ids never collide) and gitignored.
