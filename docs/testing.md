# Testing

## Run

```bat
__ctrl__\fast-rio-ctrl.bat test all
__ctrl__\fast-rio-ctrl.bat test backend
__ctrl__\fast-rio-ctrl.bat test frontend
```

## Backend

- Framework: pytest + FastAPI `TestClient`
- Location: `tests/backend/` mirrors `backend/app/modules/`
- Database: real Postgres on `localhost:5432` (start infra first)

```bat
cd backend
set PYTHONPATH=.;..\tests\backend
pytest ..\tests\backend\ -v
```

Session fixture seeds superuser and cleans sample data between runs.

## Frontend

- Framework: pytest
- Location: `tests/frontend/` — config helpers (`src.config`)

```bat
set PYTHONPATH=frontend
pytest tests\frontend -v
```

## After schema changes

1. Add migration under `backend/app/alembics/core/versions/`
2. Update `included_tables` in `env.py` if new table
3. Reset dev DB if needed: `dev purge infra` → `dev run infra`
4. Run `test backend`

## What to test

- API behavior (status codes, auth, validation)
- Service business rules when non-trivial
- Worker task functions (direct `asyncio.run` for unit tests)

Do not test trivial pass-through getters.
