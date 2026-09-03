# Dashboard UI conventions

FoxG foundation kits (**Fast-Next**, **Fast-Svelte**, **Fast-Rio**) share the same dashboard UX. Each kit implements the design in its own frontend stack — there is no shared UI package.

## Layout

- **Sidebar** (left): navigation links
- **Header** (top): theme toggle, user menu, logout
- **Main content**: page-specific UI

## Routes

| Path | Purpose | Auth |
|------|---------|------|
| `/login` | Centered login / signup | Public |
| `/` | Dashboard home (health checks) | Required |
| `/sample/notes` | Canonical notes CRUD | Required |
| `/admin` | Superuser placeholder | Superuser only |

## Visual language

- **Default theme:** dark
- **Toggle:** light/dark persisted per kit (localStorage, UserSettings, or equivalent)
- **Palette:** zinc/slate backgrounds, sky (`#0ea5e9`) primary accent
- **Sample Notes:** table/card CRUD styled like the [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) Items page

## Navigation items

1. Dashboard → `/`
2. Sample Notes → `/sample/notes`
3. Admin → `/admin` (visible only when `is_superuser`)

## Auth

- JWT via `POST /base/login/access-token`
- Profile via `GET /base/login/me`
- Dev signup via `POST /private/users/` (local only)
- Unauthenticated users redirect to `/login`

## Kit-specific implementation

| Kit | Shell location |
|-----|----------------|
| Fast-Next | `frontend/src/components/layout/`, `frontend/src/app/(dashboard)/` |
| Fast-Svelte | `frontend/src/lib/components/layout/`, `frontend/src/routes/(dashboard)/` |
| Fast-Rio | `frontend/src/components/sidebar.py`, `frontend/src/components/root_component.py` |

Do not copy UI code between kits. Match behavior and visuals only. Shared-layer (non-UI) changes transfer to all four kits — see [fast-template/README.md](../../README.md).
