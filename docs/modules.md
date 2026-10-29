# Modules

Product features live in **app modules** — one ownership boundary per feature.

Before creating a new pattern, inspect the **canonical `sample` module** (notes CRUD). It is the reference implementation for how features are structured in Fast-Rio.

## Locations

| Layer | Path |
|-------|------|
| Backend | `backend/app/modules/apps/<name>/` |
| Frontend client | `frontend/src/modules/apps/<name>/` |
| Rio page | `frontend/src/pages/<name>_page.py` |
| Tests | `tests/backend/apps/<name>/` |

Platform code (not your product): `modules/base/` (auth), `modules/system/` (health).

## Backend layers

Use only what the feature needs:

```
Router → Service → Repository → Database
```

| File | When |
|------|------|
| `router.py` | Always — HTTP endpoints |
| `service.py` | Business rules, validation, orchestration |
| `repository.py` | Database queries |
| `models.py` | SQLModel tables |
| `schemas.py` | API input/output |

Register the router in `backend/app/modules/apps/router.py`.

Naming and cross-module rules: [conventions.md](conventions.md).

## Scaffold

```bat
__ctrl__\fast-rio-ctrl.bat app create myfeature
```

Creates router, frontend stub, and test. Extend using the sample module as reference.

## Canonical example: `sample`

The **notes** module is the reference implementation. Inspect before building anything new:

| Step | Location |
|------|----------|
| Model | `backend/app/modules/apps/sample/models.py` |
| Migration | `backend/app/alembics/core/versions/002_sample_notes.py` |
| Repository | `backend/app/modules/apps/sample/repository.py` |
| Service | `backend/app/modules/apps/sample/service.py` |
| Router | `backend/app/modules/apps/sample/router.py` |
| API client | `frontend/src/modules/apps/sample/api.py` |
| Rio UI | `frontend/src/pages/sample_notes_page.py` |
| Tests | `tests/backend/apps/sample/test_notes.py` |

UI: http://dashboard.localhost/sample/notes

## Rules

- Keep feature code in the feature module — avoid scattering helpers globally.
- Simple features stay simple — do not add empty layers for ceremony.
- Add a migration when the schema changes (see [database.md](database.md)).
- Add tests for meaningful behavior (see [testing.md](testing.md)).
