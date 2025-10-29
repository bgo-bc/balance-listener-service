from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from app.nats_publisher import nats_publisher
from app.utils.queue import TaskQueue
from app.task_scheduler import TaskScheduler
from app.worker_pool import WorkerPool
from app.task_handler import FetchTaskHandler
from app.type_defs import ListenRequest
from app.ws_handler import WebsocketHandler
from app.account_registry import POLLING_ACCOUNTS, STREAMING_ACCOUNTS
from app.utils.logging import get_logger

logger = get_logger("balance_listener_service")

# Shared async queue for the scheduler and worker instances
TASK_QUEUE = TaskQueue()

scheduler: TaskScheduler = None
worker_pool: WorkerPool = None
ws_handler: WebsocketHandler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler, worker_pool, ws_handler

    logger.info("Starting Balance Aggregator app")

    scheduler = TaskScheduler(POLLING_ACCOUNTS, TASK_QUEUE)
    await scheduler.start()

    task_handler = FetchTaskHandler()
    worker_pool = WorkerPool(TASK_QUEUE, task_handler, worker_count=4)
    await worker_pool.start()

    await nats_publisher.connect()

    ws_handler = WebsocketHandler()
    await ws_handler.start()

    yield

    logger.info("Shutting down Balance Aggregator app")
    
    await scheduler.stop()
    await worker_pool.stop()
    await nats_publisher.disconnect()
    await ws_handler.stop()


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


@app.post("/stream/start")
async def start_streaming(req: ListenRequest):
    global ws_handler

    key = req.account_id
    if key in STREAMING_ACCOUNTS:
        logger.warning(f"Already streaming for account[{req.account_id}]")

    STREAMING_ACCOUNTS[key] = req.model_dump()

    logger.info(f"Streaming balance of account[{req.account_id}]")
    await ws_handler.watch_account(req.account_id)

    return {"status": "ok", "listening_key": req.account_id}


@app.post("/stream/stop")
async def stop_streaming(req: ListenRequest):
    global ws_handler

    key = req.account_id
    if key not in STREAMING_ACCOUNTS:
        raise HTTPException(status_code=404, detail="Not found")

    logger.info(f"Stopping to stream balance of account[{req.account_id}]")
    await ws_handler.unwatch_account(req.account_id)

    del STREAMING_ACCOUNTS[key]
    
    return {"status": "stopped", "listening_key": req.account_id}
