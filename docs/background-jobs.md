# Background Jobs

Fast-Rio uses **Redis + ARQ** as the standard background processing path. This is the only queue system — do not add Celery, RQ, or parallel worker architectures.

## When to use background jobs

Enqueue work when it should not block the HTTP request:

- Long-running operations
- Queued or scheduled tasks
- File processing
- External API calls
- Email or notification delivery
- Generated content
- AI inference or generation
- Cleanup and maintenance

Product-specific tasks belong in app modules but register in `WorkerSettings`.

## Layout

| Path | Role |
|------|------|
| `backend/app/core/arq.py` | Redis settings, `create_arq_pool()` |
| `backend/app/worker/worker.py` | `WorkerSettings` — register task functions |
| `backend/app/worker/tasks.py` | Task implementations |

## Dev

**Full runtime** starts the worker on the host:

```bat
__ctrl__\fast-rio-ctrl.bat dev run all
```

Worker console title: `fast-rio-worker` (Windows).

**Slim runtime** does not start Redis or the worker. See [runtime-profiles.md](runtime-profiles.md).

## Production

`compose.yml` includes a `worker` service:

```yaml
command: ["arq", "app.worker.worker.WorkerSettings"]
```

## Adding a task

1. Implement async function in `backend/app/worker/tasks.py`
2. Register in `WorkerSettings.functions` in `worker.py`:

```python
from arq.worker import func
from app.worker.tasks import my_task

class WorkerSettings:
    functions = [func(my_task, max_tries=3), ...]
```

3. Enqueue from a service (not router):

```python
from app.core.arq import create_arq_pool

pool = await create_arq_pool()
try:
    await pool.enqueue_job("my_task", arg1, arg2)
finally:
    await pool.aclose()
```

Use the function name as the job name (ARQ default).

## Test enqueue (local only)

```http
POST /api/v1/private/jobs/ping/?message=hello
```

Requires Full runtime (Redis + worker). Available only when `ENVIRONMENT=local`.

## Rules

- One queue system: ARQ. Do not add Celery, RQ, or custom queue abstractions in parallel.
- Keep tasks generic in core; product-specific tasks belong in app modules but register in `WorkerSettings`.
- Log failures in the task; use `logger = logging.getLogger(__name__)`.
- Do not add product-specific workers to the core worker file without a generality reason.
