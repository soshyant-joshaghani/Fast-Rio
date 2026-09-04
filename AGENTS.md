# AGENTS.md — AI Development Contract

Read this file **first** before making architectural changes in Fast-Rio.

Fast-Rio is a **product-agnostic Python full-stack foundation** (Rio UI + FastAPI + PostgreSQL + Redis/ARQ). Your job is to implement features **inside** the existing architecture — not redesign it.

## Start here

When asked to build a feature, answer these before writing code:

| Question | Answer |
|----------|--------|
| What to read first? | This file → [docs/architecture.md](docs/architecture.md) → [docs/conventions.md](docs/conventions.md) |
| What architecture to follow? | Router → Service → Repository → Database (see below) |
| Where does the feature belong? | `backend/app/modules/apps/<name>/` + `frontend/src/modules/apps/<name>/` |
| Is there a similar feature? | Inspect `modules/apps/` — reuse patterns |
| Should I scaffold? | Yes for new app modules: `__ctrl__\fast-rio-ctrl.bat app create <name>` |
| Where does business logic go? | `service.py` |
| Where does database logic go? | `repository.py` |
| How are API schemas handled? | `schemas.py` — separate from `models.py` |
| How is the Rio frontend structured? | `frontend/src/modules/apps/<name>/api.py` + `frontend/src/pages/<name>_page.py` |
| How are DB changes migrated? | Alembic in `backend/app/alembics/core/versions/` + `env.py` whitelist |
| Where do tests go? | `tests/backend/` mirroring module paths |
| How are background jobs added? | `backend/app/worker/tasks.py` + register in `worker.py` — see [background-jobs.md](docs/background-jobs.md) |
| How to run the project? | `__ctrl__\fast-rio-ctrl.bat dev run all` — see [cli.md](docs/cli.md) |
| Full or Slim runtime? | Full if feature needs background jobs; Slim otherwise — see [runtime-profiles.md](docs/runtime-profiles.md) |

## Before you write code

1. Read [ROADMAP.md](ROADMAP.md) for project philosophy.
2. Read [docs/architecture.md](docs/architecture.md) for structure and layer responsibilities.
3. Read [docs/conventions.md](docs/conventions.md) for naming, responses, and cross-module rules.
4. Read relevant docs: [modules.md](docs/modules.md), [background-jobs.md](docs/background-jobs.md), [runtime-profiles.md](docs/runtime-profiles.md).
5. Inspect the **canonical example** at `backend/app/modules/apps/sample/` and `frontend/src/modules/apps/sample/`.
6. Inspect any existing module that solves a similar problem — reuse its patterns.

Do **not** invent a new architecture per feature. Do **not** explain to the developer where files go — put them in the right place.

Sibling kits (Fast-Next, Fast-Svelte, Fast-Nuxt, Fast-Rio) stay in sync on shared layers. Backend / `__ctrl__` / infra / UX-contract changes transfer to all four. Frontend UI stays in this kit. Policy: [../README.md](../README.md).

## Where things go

| Kind | Location |
|------|----------|
| App feature (backend) | `backend/app/modules/apps/<name>/` |
| App feature (frontend) | `frontend/src/modules/apps/<name>/` |
| Rio page routes | `frontend/src/pages/<name>_page.py` |
| Platform auth/users | `backend/app/modules/base/` |
| System/health | `backend/app/modules/system/` |
| Shared config | `backend/app/core/config.py`, `.env` |
| Migrations | `backend/app/alembics/core/versions/` |
| Backend tests | `tests/backend/` (mirror module paths) |
| Frontend tests | `tests/frontend/` |
| Background tasks | `backend/app/worker/tasks.py` + register in `worker.py` |
| `__ctrl__` CLI | [`docs/cli.md`](docs/cli.md) — do not invent ad-hoc docker scripts |

## Scaffolding

Prefer the official generator for new app modules:

```bat
__ctrl__\fast-rio-ctrl.bat app create myfeature
```

Then extend with layers as needed (see sample module).

## Backend layers

Use this flow for app modules:

    Router → Service → Repository → Database

| Layer | Responsibility |
|-------|----------------|
| **Router** | HTTP, auth deps, request/response, call service |
| **Service** | Business rules, validation, orchestration |
| **Repository** | Queries and persistence only |
| **Models** | SQLModel table definitions |
| **Schemas** | API input/output contracts |

Rules:

- Do **not** put business logic in routers or repositories.
- Keep API schemas separate from database models unless there is a clear reason to merge them.
- Register new routers in `backend/app/modules/apps/router.py`.

## Error boundary (intentional decision)

Fast-Rio uses the **simple approach**: services raise `HTTPException` for business/API errors.

| Context | Approach |
|---------|----------|
| Business errors (not found, forbidden, validation) | `HTTPException` in **service** layer |
| Auth failures | `HTTPException` in deps/routers |
| Worker task failures | Log + ARQ `max_tries` retry |
| Unexpected exceptions | FastAPI default 500 handling |

Do **not** introduce a separate application-exception hierarchy or custom error envelope per module. Use `logging.getLogger(__name__)` for non-trivial operations.

## Frontend

- Rio is first-class — implement UI in the feature module, not scattered globals.
- Use `frontend/src/modules/apps/<name>/api.py` for HTTP clients.
- Use `@rio.page` in `frontend/src/pages/` for routes.
- Reuse shell auth from `frontend/src/modules/base/`.

## Database changes

When you add or change a table:

1. Add/update the SQLModel in the feature's `models.py`.
2. Create an Alembic migration in `backend/app/alembics/core/versions/`.
3. Add the table name to `included_tables` in `backend/app/alembics/core/env.py`.
4. Import the model in `env.py` so metadata is available.

## Tests

- Add backend tests under `tests/backend/` mirroring the module path.
- Test meaningful business logic and API behavior — not trivial getters.
- Run: `__ctrl__\fast-rio-ctrl.bat test backend`

## Configuration

- Secrets and credentials: `.env` (never commit secrets).
- Application settings: `backend/app/core/config.py`.
- Do not scatter `os.environ` reads across the codebase.

## Background jobs

- ARQ + Redis is the **only** background job mechanism — do not add Celery, RQ, or parallel queue systems.
- Register tasks in `backend/app/worker/tasks.py` and `backend/app/worker/worker.py`.
- Enqueue from **services** via `app.core.arq.create_arq_pool()` — not from routers.
- **Full runtime** starts Redis + ARQ worker; **Slim** skips both (official lightweight mode).
- Job enqueue endpoints return `503` when Redis is unavailable (expected in Slim).

See [docs/background-jobs.md](docs/background-jobs.md).

## Redis read-cache

- **Must** use `app.core.cache` (`cache_get` / `cache_set` / `cache_delete_prefix`) for hot **shared/public** reads whenever Redis is reachable (full profile / production).
- Soft-degrade: if Redis is missing (slim) or unreachable, helpers no-op and services hit Postgres — no `REDIS_CACHE_ENABLED` flag.
- Invalidate on writes (`cache_delete_prefix("<domain>:v1:")`). Canonical reference: Fast-Shop `catalog` service (`invalidate_catalog_cache`).
- **Do not** cache auth, cart, orders, or payments.
- The `sample` notes module **must** use `app.core.cache` (list/get + invalidate on write) — it is the canonical agent showcase when Redis is available.

## CLI

Development is operated through `__ctrl__/` — the project control layer:

```bat
__ctrl__\fast-rio-ctrl.bat dev run all          # full runtime (Redis + ARQ worker)
__ctrl__\fast-rio-ctrl.bat dev run all --slim   # slim runtime (no Redis/worker)
__ctrl__\fast-rio-ctrl.bat app create myfeature  # scaffold new module
__ctrl__\fast-rio-ctrl.bat test all
```

See [Readme.md](Readme.md) and [docs/cli.md](docs/cli.md) for full CLI usage.

## What you must NOT do

- Do **not** turn Fast-Rio into a product-specific template (AI app, CMS, SaaS, e-commerce, etc.).
- Do **not** invent a second pattern when one already exists.
- Do **not** modify core infrastructure (`__ctrl__/`, compose files, Traefik) for a feature-specific need unless explicitly asked.
- Do **not** add dependencies without a clear reason.
- Do **not** over-engineer — use the smallest correct change.
- Do **not** introduce FoxG-style `{ "code", "data", "meta" }` response envelopes — use FastAPI `response_model` and `HTTPException`.
- Do **not** add Admin/`User*` module naming or full RBAC unless the product explicitly requires it in an app module.

## FoxG `.rules/` (parent monorepo)

FoxG has separate architecture rules (admin CRUD, RBAC, custom responses). **Do not copy those into Fast-Rio core.** Use [docs/conventions.md](docs/conventions.md) for Fast-Rio-specific naming and boundaries.

## Canonical reference

The **sample notes module** is the reference implementation. Inspect before implementing a new feature:

```
backend/app/modules/apps/sample/
├── models.py        → Note table
├── schemas.py       → NoteCreate, NoteUpdate, NotePublic
├── repository.py    → DB access
├── service.py       → Business rules (+ HTTPException)
└── router.py        → HTTP endpoints

frontend/src/modules/apps/sample/
└── api.py           → HTTP client

frontend/src/pages/sample_notes_page.py  → Rio UI

tests/backend/apps/sample/test_notes.py  → API tests
```

Not every feature needs every layer. Match the sample module's depth when building similar CRUD features.

## Definition of done

A feature is complete when it has the appropriate layers for its complexity:

- [ ] Correct module location
- [ ] Router / service / repository as needed
- [ ] Migration (if database changes)
- [ ] API schemas
- [ ] Auth where required
- [ ] Rio UI (if user-facing)
- [ ] Tests for meaningful behavior
- [ ] Background job (if async work required)
- [ ] Logging for non-trivial operations
- [ ] Documentation updated if workflow or behavior changed

## When in doubt

> Reuse existing conventions. Prefer the smallest change that correctly implements the request.
