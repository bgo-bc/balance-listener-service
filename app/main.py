from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from app.utils.queue import TaskQueue
from app.task_scheduler import Scheduler
from app.worker_pool import WorkerPool
from app.task_handler import TaskProcessor
from app.type_defs import ListenRequest
from app.utils.logging import get_logger

logger = get_logger("balance_listener_service")

# In-memory registry of accounts that are "listening"
# For production, this can be persisted (DB) and driven by durable queue
LISTENING_ACCOUNTS: dict[str, dict] = {}

# Shared async queue for the scheduler and worker instances
TASK_QUEUE = TaskQueue()

scheduler: Scheduler = None
worker_pool: WorkerPool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler, worker_pool

    logger.info("Starting Balance Aggregator app")

    scheduler = Scheduler(LISTENING_ACCOUNTS, TASK_QUEUE)
    await scheduler.start()

    processor = TaskProcessor()
    worker_pool = WorkerPool(TASK_QUEUE, processor, worker_count=4)
    await worker_pool.start()

    yield

    logger.info("Shutting down Balance Aggregator app")
    if scheduler:
        await scheduler.stop()
    if worker_pool:
        await worker_pool.stop()


app = FastAPI(lifespan=lifespan)


@app.post("/listen/start")
async def start_listening(req: ListenRequest):
    key = req.account_id
    if key in LISTENING_ACCOUNTS:
        raise HTTPException(status_code=400, detail="Already listening for this account")

    LISTENING_ACCOUNTS[key] = req.account_id
    logger.info(f"Monitoring balance of account[{req.account_id}]")
    return {"status": "ok", "listening_key": key}


@app.post("/listen/stop")
async def stop_listening(req: ListenRequest):
    key = req.account_id
    if key not in LISTENING_ACCOUNTS:
        raise HTTPException(status_code=404, detail="Not found")

    logger.info(f"Stopping to monitor balance of account[{req.account_id}]")
    del LISTENING_ACCOUNTS[key]
    return {"status": "stopped", "listening_key": key}
