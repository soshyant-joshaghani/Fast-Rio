# Tests

Run via `__ctrl__` (preferred). Full guide: [docs/testing.md](../docs/testing.md).

- `backend/` — pytest against FastAPI (`tests/backend/` paths match `backend/app/modules/`)
- `frontend/` — pytest for Rio config helpers (`src.config`)

```bat
__ctrl__\fast-rio-ctrl.bat test all
__ctrl__\fast-rio-ctrl.bat test backend
__ctrl__\fast-rio-ctrl.bat test frontend
```

Or manually:

```bat
.venv\Scripts\activate
set PYTHONPATH=frontend
pytest tests\frontend -v

cd backend
set PYTHONPATH=.;..\tests\backend
pytest ..\tests\backend\ -v
```

Backend tests need the dev DB (`compose.dev.yml` → `localhost:15432`).
