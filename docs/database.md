# Database

## Connection

| Context | Host | Port |
|---------|------|------|
| Adminer (inside Docker) | `db` | `5432` |
| Host tools, pytest, IDE | `localhost` | `15432` |

Credentials: `.env` (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).

Settings URI: `backend/app/core/config.py` → `CORE_SQLALCHEMY_DATABASE_URI`

## Migrations

- Alembic config: `backend/alembic.ini`
- Revisions: `backend/app/alembics/core/versions/`
- Auto-run on dev infra start via `__ctrl__` prestart
- Prod: `backend/scripts/prestart.sh` in Docker prestart container

### Adding a migration

1. Edit/create SQLModel in feature `models.py`
2. Create revision in `versions/` (increment `down_revision`)
3. Add table to `included_tables` in `backend/app/alembics/core/env.py`
4. Import model in `env.py`

### Dev policy

After editing migration files on an existing dev volume:

```bat
__ctrl__\fast-rio-ctrl.bat dev purge infra
__ctrl__\fast-rio-ctrl.bat dev run infra
```

Or reset password without wipe:

```bash
docker compose -f compose.dev.yml exec db psql -U postgres -d app -c "ALTER USER postgres PASSWORD 'your-password';"
```

## Postgres 18 volumes

Postgres 18 declares `VOLUME /var/lib/postgresql`. Compose mounts:

```yaml
volumes:
  - db-data:/var/lib/postgresql
environment:
  PGDATA: /var/lib/postgresql/18/docker
```

If compose previously mounted a subdirectory, Docker may have created an **anonymous hex volume**. After fixing compose:

```bat
__ctrl__\fast-rio-ctrl.bat dev purge infra
docker volume rm <hex-id>   # optional, if dangling
__ctrl__\fast-rio-ctrl.bat dev run infra
```

Only `fast-rio-dev_db-data` should remain.

## Initial data

`backend/app/initial_data.py` creates the first superuser from `.env` on prestart.
