from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from app.nats_publisher import nats_publisher
from app.utils.queue import TaskQueue
from app.task_scheduler import TaskScheduler
from app.worker_pool import WorkerPool
from app.task_handler import FetchTaskHandler
from app.types import ListenRequest
from app.account_registry import POLLING_ACCOUNTS
from app.adapter import adapter_registry
from app.adapter.types import AdapterConfig
from app.utils.logging import get_logger

logger = get_logger("balance_listener_service")

# Shared async queue for the scheduler and worker instances
TASK_QUEUE = TaskQueue()

scheduler: TaskScheduler = None
worker_pool: WorkerPool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler, worker_pool

    logger.info("Starting Balance Aggregator app")

    scheduler = TaskScheduler(POLLING_ACCOUNTS, TASK_QUEUE)
    await scheduler.start()

    task_handler = FetchTaskHandler()
    worker_pool = WorkerPool(TASK_QUEUE, task_handler, worker_count=4)
    await worker_pool.start()

    await nats_publisher.connect()

    yield

    logger.info("Shutting down Balance Aggregator app")
    
    await scheduler.stop()
    await worker_pool.stop()
    await nats_publisher.disconnect()


app = FastAPI(lifespan=lifespan)


@app.post("/poll/start")
async def start_polling(req: ListenRequest):
    global scheduler

    key = req.account_id
    if key in POLLING_ACCOUNTS:
        logger.warning(f"Already listening for account[{req.account_id}]")

    POLLING_ACCOUNTS[key] = req.model_dump()

    logger.info(f"Monitoring balance of account[{req.account_id}]")
    await scheduler.enqueue_account(
        req.account_id, ["balance", "earn_balance", "positions", "option_positions", "funding_fees"]
    )

    return {"status": "ok", "listening_key": key}


@app.post("/poll/stop")
async def stop_polling(req: ListenRequest):
    key = req.account_id
    if key not in POLLING_ACCOUNTS:
        raise HTTPException(status_code=404, detail="Not found")

    logger.info(f"Stopping to monitor balance of account[{req.account_id}]")
    del POLLING_ACCOUNTS[key]
    return {"status": "stopped", "listening_key": key}


@app.post("/config/adapter")
async def add_endpoint_config(config: AdapterConfig):
    adapter_registry.register_config(config)
    return {"status": "ok"}
