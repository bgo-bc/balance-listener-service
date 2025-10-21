from typing import Any
import asyncio


class BaseQueue:
    async def put(self, item: Any) -> None:
        raise NotImplementedError()

    async def get(self) -> Any:
        raise NotImplementedError()

    async def task_done(self):
        pass


# Temporary in-memory message queue. Replaceable with Redis/NATS in the future
class TaskQueue(BaseQueue):
    def __init__(self):
        self._queue = asyncio.Queue()

    async def put(self, item):
        await self._queue.put(item)

    async def get(self):
        return await self._queue.get()

    async def task_done(self):
        self._queue.task_done()
