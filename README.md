[![](https://github.com/soshyant-joshaghani/Fast-Rio/raw/main/Fast-System.png?raw=true)](https://github.com/soshyant-joshaghani/Fast-Rio)

[![](https://github.com/soshyant-joshaghani/Fast-Rio/raw/main/Fast-Rio.png?raw=true)](https://github.com/soshyant-joshaghani/Fast-Rio)

# Fast-Rio

**A modular, opinionated full-stack Python foundation for building and deploying services.**

Structured for developers. Guided for AI. From idea to deployable service.

Fast-Rio is a **product-agnostic launchpad** — not a finished product and not a domain-specific template. Use the same foundation for dashboards, CRUD apps, APIs, SaaS products, background-processing services, or AI-powered applications. The difference is the **modules you add**, not a different project architecture.

**Documentation:** [AGENTS.md](AGENTS.md) · [ROADMAP.md](ROADMAP.md) · [docs/](docs/)

---

## What Fast-Rio provides

Fast-Rio answers repeated architectural and infrastructure questions before development starts:

| Pillar | What you get |
|--------|--------------|
| **Architecture** | Modular backend (FastAPI) + frontend (Rio) with clear layer boundaries |
| **Modularity** | App modules with a canonical reference implementation |
| **Project control** | `__ctrl__` CLI — one interface for dev, test, and deploy |
| **AI guardrails** | [AGENTS.md](AGENTS.md) — conventions agents follow instead of reinventing structure |
| **Development workflow** | Hot reload, scaffolding, local tooling |
| **Testing** | pytest layout mirroring modules |
| **Deployment** | SSH/VM workflow from laptop to production |

You provide product requirements, features, business rules, UI needs, and integrations. Fast-Rio provides structure, conventions, lifecycle control, background processing, testing, and deployment.

> **Python = Full Stack.** Rio for UI. FastAPI for API. PostgreSQL for data. Redis + ARQ for background jobs. `__ctrl__` for the workflow.

---

## Why it exists

Building a service usually means re-deciding the same things: project layout, module boundaries, database migrations, auth, background jobs, testing, and deployment. Fast-Rio makes those decisions once — so you and AI agents can focus on the product.

```text
Idea
  ↓
Fast-Rio (foundation + guardrails)
  ↓
AI-assisted development
  ↓
Modular implementation
  ↓
Testing
  ↓
Deployment
  ↓
Working service
```

Fast-Rio does not build products for you. It provides the runway; AI helps implement features **inside** the existing architecture.

---

## Architecture at a glance

```text
Fast-Rio
│
├── Application Layer
│   ├── Frontend (Rio)          frontend/src/
│   └── Backend (FastAPI)     backend/app/modules/
│
├── Infrastructure Layer
│   ├── PostgreSQL + Alembic
│   ├── Redis + ARQ workers
│   ├── Traefik (routing / TLS)
│   └── Docker Compose
│
└── Control Layer
    └── __ctrl__/               dev · test · deploy · scaffold
```

**Backend flow:** Router → Service → Repository → Database

**Canonical example:** the `sample` notes module — inspect before creating new patterns. UI: http://dashboard.localhost/sample/notes

Details: [docs/architecture.md](docs/architecture.md) · [docs/modules.md](docs/modules.md)

---

## Stack

| Layer | Tech | Dev URL |
|-------|------|---------|
| Frontend | Rio (`rio-ui`) — Python UI | http://dashboard.localhost |
| Backend | FastAPI + SQLModel + Alembic | http://api.localhost/docs · http://api.localhost/sdoc |
| Database | Postgres 18 | localhost:15432 |
| Jobs | ARQ + Redis 8 | localhost:16379 · worker on host (full runtime) |
| Proxy | Traefik 3.6 | http://localhost:18090 |
| Adminer | Adminer (via Traefik) | http://adminer.localhost |

---

## Runtime profiles

Both are **official** supported modes — not “full vs broken.”

| Profile | Command | Includes |
|---------|---------|----------|
| **Full** | `dev run all` | Postgres, Redis, ARQ worker, Traefik, Adminer, uvicorn, Rio |
| **Slim** | `dev run all --slim` | Postgres, Traefik, Adminer, uvicorn, Rio (no Redis / no worker) |

- **Full** — background jobs, queues, async work, or when you want the complete stack locally.
- **Slim** — CRUD, auth, simple APIs, faster startup, lower resource use. A valid lightweight profile, not a workaround.

Production always runs the full stack (Postgres, Redis, worker). See [docs/runtime-profiles.md](docs/runtime-profiles.md).

---

## Quick start (dev)

From `fast-rio/`:

```bat
__ctrl__\fast-rio-ctrl.bat setup-local
__ctrl__\fast-rio-ctrl.bat dev run all
```

| Service | URL |
|---------|-----|
| Dashboard | http://dashboard.localhost |
| Sample Notes (canonical example) | http://dashboard.localhost/sample/notes |
| API (Swagger) | http://api.localhost/docs |
| API (Scalar) | http://api.localhost/sdoc |
| Adminer | http://adminer.localhost |
| Traefik | http://localhost:18090 |
| Direct Rio | http://localhost:3000 |
| Direct API | http://localhost:18000/docs |

Linux/mac:

```bash
chmod +x __ctrl__/fast-rio-ctrl.sh
__ctrl__/fast-rio-ctrl.sh setup-local
__ctrl__/fast-rio-ctrl.sh dev run all
```

Stop: `__ctrl__\fast-rio-ctrl.bat dev stop all`

**Port 80/443 conflict:** only one Traefik-on-`:80` stack at a time. Stop the other proxy or run apps only: `dev run apps` (direct `http://localhost:3000` / `http://localhost:18000/docs`).

---

## AI-assisted development

1. Start the project (`dev run all` or `--slim` as appropriate)
2. Point the AI at [AGENTS.md](AGENTS.md) and the **sample** module
3. AI implements inside existing layers — no architecture reinvention
4. Run `test all` before deploy

The developer provides product rules and UI requirements. The AI reads guardrails and inspects `backend/app/modules/apps/sample/` before building.

See [docs/development.md](docs/development.md).

---

## Adding a feature

1. Inspect the **canonical sample module** (`sample` — notes CRUD)
2. Scaffold (recommended): `__ctrl__\fast-rio-ctrl.bat app create myfeature`
3. Backend: `backend/app/modules/apps/<name>/`
4. Frontend: `frontend/src/modules/apps/<name>/` + `frontend/src/pages/`
5. Migration if schema changes; tests under `tests/backend/`

Use the smallest appropriate implementation. Not every feature needs every layer — match the sample module's depth for similar CRUD features.

### Frontend modules (mandatory)

Under the frontend modules root (`frontend/src/modules/`) there are **only**:

- `base/` — kit/platform (auth, users, shell, stores) + design primitives at `base/ui/`
- `apps/<domain>/` — product domains (API clients + UI), mirroring `backend/app/modules/apps/<domain>/`

There is **no** project `components/` folder as the app UI home. Modules are the component home.
Do not add `global/`, `shell/`, `layout/`, or a top-level `modules/ui/` peer of `base`/`apps`.

---

## Project layout

```
fast-rio/
├── AGENTS.md                 # AI development contract
├── ROADMAP.md                # Vision and principles
├── __ctrl__/                 # Control layer — dev, test, deploy (see docs/cli.md)
├── compose.dev.yml           # Dev infra (db, redis, Traefik, adminer)
├── compose.yml               # Production stack
├── backend/app/
│   ├── core/                 # config, db, security, arq
│   ├── worker/               # ARQ WorkerSettings + tasks
│   └── modules/
│       ├── base/             # auth, users
│       ├── system/           # health, private dev routes
│       └── apps/             # your product modules (+ sample/)
├── frontend/src/
│   ├── modules/base/         # kit/platform (auth, shell, widgets) + ui/
│   ├── modules/apps/         # feature HTTP clients
│   └── pages/                # @rio.page routes
└── tests/                    # mirrors backend module paths
```

---

## Tests

```bat
__ctrl__\fast-rio-ctrl.bat test all
```

Backend needs dev DB (`dev run infra` → `localhost:15432`). See [docs/testing.md](docs/testing.md).

After Alembic or Postgres volume changes: `dev purge infra`, then `dev run infra`.

---

## Production

From laptop (SSH):

```bat
__ctrl__\fast-rio-ctrl.bat setup
__ctrl__\fast-rio-ctrl.bat clone
__ctrl__\fast-rio-ctrl.bat env
__ctrl__\fast-rio-ctrl.bat start
```

On VM: `bash __ctrl__/remote/setup-ubuntu.sh` then `bash __ctrl__/remote/start-prod.sh`

See [docs/deployment.md](docs/deployment.md) · [`__ctrl__/README.md`](__ctrl__/README.md)

---

## Relationship to other FoxG kits

| Kit | Role |
|-----|------|
| **Fast-Rio** (this repo) | General-purpose Python full-stack foundation (Rio UI) |
| [Fast-Next](https://github.com/soshyant-joshaghani/Fast-Next) | General-purpose foundation (Next.js UI) |
| [Fast-Svelte](https://github.com/soshyant-joshaghani/Fast-Svelte) | General-purpose foundation (SvelteKit UI) |
| [Fast-Nuxt](https://github.com/soshyant-joshaghani/Fast-Nuxt) | General-purpose foundation (Nuxt UI) |

Kits are **the same foundation with different frontends** — keep them in sync. Shared-layer changes (backend, `__ctrl__`, Alembic/ARQ/compose, dashboard UX contract) transfer to all four. Frontend-only changes stay in this kit. Do not paste React/Svelte/Vue/Rio UI between kits.

Workspace index: [fast-template/README.md](../README.md)

---

## Adminer & database

| Context | Server | Port |
|---------|--------|------|
| Adminer (browser) | `db` | `5432` |
| Host / IDE / pytest | `localhost` | `15432` |

Credentials from `.env` (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).

**Troubleshooting:** [docs/database.md](docs/database.md)

---

## Environment

Copy `.env.example` → `.env`. URLs and CORS in `compose.*.yml`; secrets in `.env`.

Default superuser: `admin@example.com` / `FIRST_SUPERUSER_PASSWORD` from `.env`.

`PUBLIC_API_BASE_URL` — where Rio calls FastAPI (server-side HTTP).

---

## Documentation index

| Doc | Answers |
|-----|---------|
| [AGENTS.md](AGENTS.md) | Rules for AI coding agents |
| [ROADMAP.md](ROADMAP.md) | Vision, principles, long-term goals |
| [docs/architecture.md](docs/architecture.md) | Layers, boundaries, core vs apps |
| [docs/modules.md](docs/modules.md) | How to build a feature module |
| [docs/cli.md](docs/cli.md) | `__ctrl__` commands |
| [docs/runtime-profiles.md](docs/runtime-profiles.md) | Full vs Slim |
| [docs/background-jobs.md](docs/background-jobs.md) | Redis, ARQ, adding tasks |
| [docs/development.md](docs/development.md) | Local workflow, AI-assisted dev |
| [docs/testing.md](docs/testing.md) | pytest, test layout |
| [docs/database.md](docs/database.md) | Migrations, Adminer, volumes |
| [docs/deployment.md](docs/deployment.md) | Dev → production path |
| [docs/conventions.md](docs/conventions.md) | Naming, API responses, cross-module rules |
