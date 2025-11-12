from pydantic import BaseModel
from typing import Any, Dict, List, Protocol


class ListenRequest(BaseModel):
    account_id: str


class FetchTask(BaseModel):
    account_id: str
    types: List[str]


class TaskProcessor(Protocol):
    async def process(self, task: Dict[str, Any]) -> None: ...
