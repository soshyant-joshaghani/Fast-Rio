# Conventions

Naming, layers, and cross-module rules for Fast-Rio. Follow these in app modules; platform code (`base/`, `system/`) sets the baseline.

## Naming

| Element | Style | Example |
|---------|-------|---------|
| Files / folders | `snake_case`, lowercase | `sample_notes_page.py`, `repository.py` |
| Classes | `PascalCase`, singular | `Note`, `NoteCreate`, `SampleNotesPage` |
| Functions / variables | `snake_case`, verb-based | `create_note`, `get_note_by_id`, `owner_id` |
| Booleans | `is_`, `has_`, `can_` prefix | `is_active`, `is_superuser` |
| Constants | `UPPER_SNAKE_CASE` | module-level only when truly constant |
| API routes | plural nouns, REST-ish | `GET /sample/notes/`, `POST /sample/notes/` |

### Schema suffixes

| Purpose | Pattern | Example |
|---------|---------|---------|
| Create body | `<Entity>Create` | `NoteCreate` |
| Update body | `<Entity>Update` | `NoteUpdate` |
| API response | `<Entity>Public` or descriptive name | `NotePublic` |
| List filters (if needed) | `<Entity>Filter` | `NoteFilter` |

Avoid vague names (`data`, `info`, `temp`, `handle`).

## Backend layers

```
Router → Service → Repository → Database
```

| Layer | Allowed | Not allowed |
|-------|---------|-------------|
| **Router** | HTTP, deps, call service, return schemas | Business logic, SQL |
| **Service** | Rules, validation, `HTTPException`, orchestration | Raw SQL (use repository) |
| **Repository** | Queries, CRUD | Business rules, HTTP |
| **Models** | SQLModel tables | FastAPI imports |
| **Schemas** | API contracts | Database access |

Simple features may omit service or repository — see the sample module for CRUD depth.

## API responses and errors

Fast-Rio uses **standard FastAPI**, not a custom envelope.

- Return Pydantic/SQLModel types via `response_model=`
- Errors: `HTTPException(status_code=..., detail="...")` in the **service** layer
- HTTP status on the response; do not embed status codes in JSON bodies

**Intentional decision:** Fast-Rio uses the simple approach — services raise `HTTPException` directly. Do not introduce a separate application-exception hierarchy unless a product module explicitly requires it.

Do **not** introduce FoxG-style `{ "code": "SUCCESS", "data": {}, "meta": {} }` wrappers unless an app module explicitly requires that contract.

## Cross-module relations

Fast-Rio modules: `base/` (platform), `system/`, `apps/<feature>/`.

| Relation | Guidance |
|----------|----------|
| App module → **platform** (`user.id`) | OK — e.g. `Note.owner_id` FK to `user` |
| App module ↔ **app module** | Avoid FKs and ORM `relationship()` across app modules |
| Cross-app data | Call the other module's **service** (or repository via service), not direct model imports in repositories |

### Populate (nested objects in responses)

- Store **IDs** in the database
- Resolve related objects in **service** (or build response schemas there)
- Do not rely on cross-module SQLAlchemy joins

Example: returning a note with owner email → service loads user via `base` users layer, not a join from `Note` to foreign app tables.

## Nested routers (optional)

Flat registration is the default:

```python
# backend/app/modules/apps/router.py
apps_router.include_router(sample_router)
```

If a domain grows nested folders (`apps/shop/orders/`), each logical level may define a router and register **bottom-up** into the parent. Do not skip levels or register leaf routers directly in `main.py`.

## Auth (what exists today)

- `CurrentUser` — authenticated user
- `SuperAdminUser` — `is_superuser=True`

There is **no** built-in RBAC (per-module Get/Create/Update/Delete permissions). If a product needs that, implement it inside the app module's service layer — do not assume FoxG-style role matrices in core.

## Product-specific patterns (not in core)

These belong in **app modules**, not Fast-Rio foundation docs or core code:

- Admin vs `User*` module naming (`Currency` / `UserCurrency`)
- Mandatory admin CRUD with search/sort/pagination standards
- Global `{ code, data, meta }` response envelopes
- Metadata fields used for backend logic

See [AGENTS.md](../AGENTS.md) and [modules.md](modules.md).
