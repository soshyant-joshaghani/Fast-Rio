# Frontend (Rio)

Python UI via [rio-ui](https://pypi.org/project/rio-ui/) — no HTML/CSS/JS.

**Canonical example:** `src/modules/apps/sample/` + `src/pages/sample_notes_page.py` — inspect before building new UI features.

## Layout

```
frontend/
├── rio.toml                 # main-module = src
└── src/
    ├── __init__.py          # rio.App
    ├── config/              # API_BASE_URL
    ├── modules/base/        # kit/platform (auth, shell, widgets)
    │   └── ui/              # small widget primitives
    ├── modules/apps/        # per-app UI modules
    └── pages/               # @rio.page routes
```

### Frontend modules (mandatory)

Under the frontend modules root (`src/modules/`) there are **only**:

- `base/` — kit/platform (auth, users, shell, stores) + design primitives at `base/ui/`
- `apps/<domain>/` — product domains (API clients + UI), mirroring `backend/app/modules/apps/<domain>/`

There is **no** project `components/` folder as the app UI home. Modules are the component home.
Do not add `global/`, `shell/`, `layout/`, or a top-level `modules/ui/` peer of `base`/`apps`.

## Dev

From repo root (after `fast-rio-ctrl setup-local`):

```bat
cd frontend
set PUBLIC_API_BASE_URL=http://localhost:18000/api/v1
rio run --port 5000
```

Or use `__ctrl__\fast-rio-ctrl.bat dev run all` (starts Traefik + API + Rio).

Traefik: http://dashboard.localhost → Rio :5000

## Production

`Dockerfile` runs `rio run --port 5000 --release`.

Set `PUBLIC_API_BASE_URL` at runtime (compose uses `http://backend:8000/api/v1` on the Docker network).

## Local desktop app

Root `requirements.txt` installs `rio-ui[window]` (pywebview / PySide6). From `frontend/`:

```bat
set PYTHONPATH=%CD%
set PUBLIC_API_BASE_URL=http://localhost:18000/api/v1
python -c "import src; src.app.run_in_window()"
```
