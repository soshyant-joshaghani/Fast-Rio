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
    ├── modules/shell/       # auth shell + helpers
    ├── modules/apps/        # per-app UI modules
    ├── components/          # RootComponent + Navbar
    └── pages/               # @rio.page routes
```

## Dev

From repo root (after `fast-rio-ctrl setup-local`):

```bat
cd frontend
set PUBLIC_API_BASE_URL=http://localhost:18000/api/v1
rio run --port 3000
```

Or use `__ctrl__\fast-rio-ctrl.bat dev run all` (starts Traefik + API + Rio).

Traefik: http://dashboard.localhost → Rio :3000

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
