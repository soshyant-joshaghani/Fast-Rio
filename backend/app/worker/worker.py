from arq.worker import func

from app.core.arq import get_redis_settings
from app.worker.tasks import ping


class WorkerSettings:
    functions = [func(ping, max_tries=3)]
    redis_settings = get_redis_settings()
