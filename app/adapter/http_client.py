
import httpx
from typing import Optional, Dict, Any
from app.utils.logging import get_logger

logger = get_logger("http_client")

class HttpClient:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    async def fetch(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request("GET", url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
