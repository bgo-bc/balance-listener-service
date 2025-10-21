import asyncio
from typing import List
from app.type_defs import TaskProcessor
from app.utils.logging import get_logger


logger = get_logger("worker_pool")


class WorkerPool:
    def __init__(self, queue: asyncio.Queue, processor: TaskProcessor, worker_count: int = 4):
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
            logger.info(f"Workers stopped")
        except Exception as e:
            logger.warning(f"Error while waiting for worker to end: {e}")
            pass

    async def _worker_loop(self, worker_id: int):
        while not self._stopped.is_set():
            try:
                task = await self.queue.get()
                if not task:
                    await asyncio.sleep(0.1)
                    continue

                logger.info(f"Worker[{worker_id}] processing task: {task}")
                await self.processor.process(task)
                await self.queue.task_done()

            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
