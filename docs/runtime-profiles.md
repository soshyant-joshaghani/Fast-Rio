# Runtime Profiles

Fast-Rio officially supports two **development** runtime profiles. Both are valid — neither is a workaround or degraded mode.

Redis and ARQ are part of the full Fast-Rio runtime. Slim is an official lightweight profile for apps that do not need background processing — not because Redis is "optional infrastructure."

## Full runtime

```bat
__ctrl__\fast-rio-ctrl.bat dev run all
```

**Infrastructure (Docker):** Postgres, Redis, Traefik, Adminer

**Apps (host):** uvicorn (API), ARQ worker, Rio (dashboard)

Use when the application needs background jobs, or when you want the complete Fast-Rio stack locally.

## Slim runtime

```bat
__ctrl__\fast-rio-ctrl.bat dev run all --slim
```

**Infrastructure (Docker):** Postgres, Traefik, Adminer — **no Redis**

**Apps (host):** uvicorn, Rio — **no ARQ worker**

Use when building features that do not need background processing (CRUD, auth, simple APIs, static-ish UIs).

Slim is intended for faster startup and lower resource use — not because Redis is “optional infrastructure.” It is an official lightweight profile.

## Production

Production (`compose.yml`) always runs the **full** stack: Postgres, Redis, ARQ worker, backend, frontend, Traefik.

There is no slim production profile.

## Choosing a profile

| Need | Profile |
|------|---------|
| Background jobs, queues, async work | Full |
| Simple CRUD / auth / API-only dev | Slim |
| Testing job enqueue locally | Full |
| CI that skips Redis | Slim (if tests do not require Redis) |

Job enqueue endpoints return `503` when Redis is unavailable (expected in Slim unless Redis is started manually).
