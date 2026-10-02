# Plan progress — Fast-Rio

**Single live tracker for agents.** Execution detail: **[EXECUTION.md](./EXECUTION.md)**.

Commit these files. `__plans__/` is part of the product history — not local scratch.

## Agent rules

1. Read **PROGRESS.md** first. Take the first `pending` stage whose blockers are `done`.
2. Mark it `in_progress` in this file **before** implementation.
3. Implement only that stage’s scope. Do not start the next stage in the same pass.
4. When the stage’s acceptance checks are met, run the relevant tests via `__ctrl__` (at minimum `test all` for the touched surface). **Do not** mark `done` if tests fail.
5. On green tests: mark the stage `done`, fill **Agent / date** and **Note**, update **Last update**, then stop or take the next eligible `pending` stage.
6. Keep frontend in the same stage when a stage changes a user-facing API.
7. Prefer feature UI under `frontend/src/modules/apps/<domain>/` with pages in `frontend/src/pages/`.

Status: `pending` | `in_progress` | `done` | `blocked` | `skipped` | `superseded`

## Critical path

```text
(replace with your product stages)
F0 → …
```

| ID | Stage | Status | Blocked by | Agent / date | Note |
|----|-------|--------|------------|--------------|------|
| F0 | Freeze product scope and first execution stages | pending | — | | Replace this row once the product plan is written |

## Foundation kept

| Area | State |
|------|-------|
| FastAPI + SQLModel + Alembic foundation | done |
| Rio UI foundation | done |
| OAuth2/JWT auth and current-user/superuser dependencies | done |
| Dashboard scaffold | done |
| Redis/ARQ full runtime and slim fallback | done |
| `app.core.cache` soft-degrading helpers | done |
| `__ctrl__` dev/test/deploy workflow | done |
| Sample notes canonical CRUD/cache example | done |

## Last update

| Field | Value |
|-------|-------|
| Updated | — |
| By | — |
| Next | Write product stages in EXECUTION.md and mirror them here |
