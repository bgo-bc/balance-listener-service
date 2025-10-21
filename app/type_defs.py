from pydantic import BaseModel
from typing import Any, Dict, Protocol


class ListenRequest(BaseModel):
    account_id: str


class BalanceTask(BaseModel):
    account_id: str
    type: str


class TaskProcessor(Protocol):
    async def process(self, task: Dict[str, Any]) -> None: ...
