# Deployment

Path from local development to production on a single VM.

```text
Development  →  Tests  →  Production compose  →  Traefik + TLS  →  Running service
```

## Prerequisites

- Ubuntu VM with Docker
- DNS A records: `@`, `api`, optional `adminer` → VM IP
- External Docker network (once per VM): `docker network create traefik-public`

## Configure

1. Copy `.env.example` → `.env` — set secrets, DB password, superuser password
2. Edit `DOMAIN` and URLs in `compose.yml` (`x-prod-app-config`)
3. Upload prod env via `__ctrl__` safe folder for SSH deploy

## First deploy (SSH from laptop)

```bat
__ctrl__\fast-rio-ctrl.bat setup
__ctrl__\fast-rio-ctrl.bat pubkey
__ctrl__\fast-rio-ctrl.bat clone
__ctrl__\fast-rio-ctrl.bat env
__ctrl__\fast-rio-ctrl.bat start
```

On VM (bootstrap):

```bash
bash __ctrl__/remote/setup-ubuntu.sh
bash __ctrl__/remote/start-prod.sh
```

## Production stack

`compose.yml` includes:

- Postgres, Redis, backend, worker (ARQ), frontend (Rio), Traefik (Let's Encrypt)
- Adminer (optional subdomain)

Traefik routes:

- `https://<domain>` → frontend
- `https://api.<domain>` → backend

## Day-2 operations

```bat
__ctrl__\fast-rio-ctrl.bat update
__ctrl__\fast-rio-ctrl.bat status
__ctrl__\fast-rio-ctrl.bat stop
__ctrl__\fast-rio-ctrl.bat backup-acme
```

Reset (wipes DB/Redis volumes, keeps SSL): see `__ctrl__/remote/reset-prod.sh`

## Local prod smoke

Windows Docker Desktop only:

```bat
__ctrl__\fast-rio-ctrl.bat prod start
```

Scripts: [`__ctrl__/remote/`](../__ctrl__/remote/README.md)

## Rio in production

Frontend container sets `PUBLIC_API_BASE_URL=http://backend:8000/api/v1` — server-side HTTP on the Docker network, not the public browser URL.
