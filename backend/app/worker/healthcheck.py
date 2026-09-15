from arq.worker import check_health

from app.worker.worker import WorkerSettings

if __name__ == "__main__":
    raise SystemExit(check_health(WorkerSettings))
