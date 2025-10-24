import asyncio
from typing import List
from app.type_defs import TaskProcessor
from app.utils.queue import TaskQueue
from app.utils.logging import get_logger


logger = get_logger("worker_pool")


class WorkerPool:
    def __init__(self, queue: TaskQueue, processor: TaskProcessor, worker_count: int = 4):
        self.queue = queue
        self.worker_count = worker_count
        self.processor = processor
        self._workers: List[asyncio.Task] = []
        self._stopped = asyncio.Event()

    async def start(self):
        self._stopped.clear()
        for i in range(self.worker_count):
            worker = asyncio.create_task(self._worker_loop(i), name=f"worker-{i}")
            self._workers.append(worker)
            logger.info(f"Worker {worker.get_name()} started")

    async def stop(self):
        self._stopped.set()
        try:
            for worker in self._workers:
                logger.info(f"Stopping {worker.get_name()}")
                worker.cancel()

            await asyncio.gather(*self._workers, return_exceptions=True)
            logger.info("Workers stopped")
        except Exception as e:
            logger.warning(f"Error while waiting for worker to end: {e}")
            pass

    async def _worker_loop(self, worker_id: int):
        try:
            while not self._stopped.is_set():
                task = await self.queue.get()
                if not task:
                    await asyncio.sleep(0.1)
                    continue

                logger.info(f"Worker[{worker_id}] processing task: {task}")

                try:
                    await self.processor.process(task)
                except asyncio.CancelledError:
                    logger.info(f"Worker[{worker_id}] was cancelled during processing.")
                    raise
                except Exception as e:
                    logger.warning(f"Worker {worker_id} error: {e}")
                finally:
                    await self.queue.task_done()
        except asyncio.CancelledError:
            logger.info(f"Worker[{worker_id}] cancelled.")
            raise
