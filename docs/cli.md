# CLI (`__ctrl__`)

`__ctrl__/` is the **control layer** for Fast-Rio — the official interface for dev, test, deploy, and SSH ops. Prefer these commands over ad-hoc `docker compose` or manual process management.

Entry points:

```bat
__ctrl__\fast-rio-ctrl.bat <command>
```

```bash
__ctrl__/fast-rio-ctrl.sh <command>
```

Full reference: [`__ctrl__/README.md`](../__ctrl__/README.md)

## Local setup

```bat
fast-rio-ctrl.bat setup-local
fast-rio-ctrl.bat setup-local --force   # recreate .venv
```

Creates project `.venv` and installs `requirements.txt`.

## Development

```bat
fast-rio-ctrl.bat dev run all
fast-rio-ctrl.bat dev run all --slim
fast-rio-ctrl.bat dev stop all
fast-rio-ctrl.bat dev down all
fast-rio-ctrl.bat dev purge infra
fast-rio-ctrl.bat dev reset all
```

| Target | Meaning |
|--------|---------|
| `infra` | Docker: db, redis (full), proxy, adminer + migrations |
| `apps` | Host: uvicorn :8000, ARQ worker (full), rio :5000 |
| `all` | Both (run order: infra → apps; stop: apps → infra) |

See [runtime-profiles.md](runtime-profiles.md) for `--slim`.

## Module scaffold

```bat
fast-rio-ctrl.bat app create myfeature
```

## Tests

```bat
fast-rio-ctrl.bat test all
fast-rio-ctrl.bat test backend
fast-rio-ctrl.bat test frontend
```

## Production (SSH from laptop)

```bat
fast-rio-ctrl.bat setup
fast-rio-ctrl.bat pubkey
fast-rio-ctrl.bat clone
fast-rio-ctrl.bat env
fast-rio-ctrl.bat start
fast-rio-ctrl.bat stop
fast-rio-ctrl.bat update
fast-rio-ctrl.bat status
fast-rio-ctrl.bat connect
```

## Local prod smoke (Docker Desktop)

```bat
fast-rio-ctrl.bat prod start
fast-rio-ctrl.bat prod stop
fast-rio-ctrl.bat prod reset
```

On-VM scripts: `__ctrl__/remote/` (invoked by SSH commands above).
