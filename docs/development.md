# Development

## Launchpad workflow

Fast-Rio is designed so you focus on product requirements, not repeated architecture decisions:

```text
Clone → setup-local → dev run all
    → give AI your feature requirements
    → AI reads AGENTS.md + inspects sample module
    → AI extends modules inside existing architecture
    → test all → deploy
```

You provide: product rules, features, UI requirements, integrations.
Fast-Rio provides: structure, conventions, control CLI, testing, deployment path.
AI helps implement the product inside the guardrails. See [AGENTS.md](../AGENTS.md).

## First run

```bat
copy .env.example .env
__ctrl__\fast-rio-ctrl.bat setup-local
__ctrl__\fast-rio-ctrl.bat dev run all
```

Choose Full or Slim: [runtime-profiles.md](runtime-profiles.md)

## Hot reload

- **API:** uvicorn `--reload` on port 8000 (host)
- **UI:** `rio run` on port 5000 (host)
- **Infra:** Docker Compose (`compose.dev.yml`)

Edit Python files; services restart automatically.

## Manual run (without `__ctrl__`)

Prefer `__ctrl__` for normal development. Use manual commands only when debugging individual services.

Infra only (full — includes Redis):

```bat
docker compose -f compose.dev.yml up -d db redis proxy adminer
```

Infra only (slim — no Redis):

```bat
docker compose -f compose.dev.yml up -d db proxy adminer
```

API only:

```bat
cd backend
set PYTHONPATH=.
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Rio only:

```bat
cd frontend
set PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
set PYTHONPATH=.
..\.venv\Scripts\python.exe -m rio run --port 5000
```

Worker (full stack):

```bat
cd backend
..\.venv\Scripts\python.exe -m arq app.worker.worker.WorkerSettings
```

## Configuration

| What | Where |
|------|-------|
| Secrets, DB/Redis credentials | `.env` |
| App settings | `backend/app/core/config.py` |
| CORS, hosts, domain | `compose.dev.yml` / `compose.yml` |
| Rio → API URL | `PUBLIC_API_BASE_URL` env var |

Do not read `os.environ` scattered across app code — use `settings` from `core/config.py`.

## Private dev routes

When `ENVIRONMENT=local`, FastAPI exposes `/api/v1/private/*` (signup without auth, job ping test). Not available in production.
