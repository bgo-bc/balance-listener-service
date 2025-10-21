from typing import Dict, Any, List
from ccxt.base.exchange import Exchange
import ccxt.async_support as ccxt
from app.utils.logging import get_logger


logger = get_logger("ccxt_adapter")


class CCXTAdapter:
    def __init__(self, exchange_id: str, credentials: dict[str, str]):
        self.exchange_id = exchange_id
        self.credentials = credentials or {}
        self.exchange: Exchange = None

    async def __aenter__(self):
        await self._init_exchange()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._close()

    async def _init_exchange(self):
        exchange_class = getattr(ccxt, self.exchange_id, None)
        if exchange_class is None:
            exchange_class = getattr(ccxt, self.exchange_id.lower(), None)
        if exchange_class is None:
            raise ValueError(f"Unsupported exchange id: {self.exchange_id}")

        params = {"enableRateLimit": True}
        if self.credentials:
            params.update(
                {
                    "apiKey": self.credentials.get("apiKey"),
                    "secret": self.credentials.get("secret"),
                }
            )
        self.exchange = exchange_class(params)
        self.exchange.set_sandbox_mode(True)

    async def _close(self):
        if self.exchange:
            try:
                await self.exchange.close()
            except Exception:
                pass
            self.exchange = None

    async def fetch_balances(self) -> List[Dict[str, Any]]:
        if not self.exchange:
            await self._init_exchange()

        raw = await self.exchange.fetch_balance()
        normalized = []

        spot = raw.get("total", {})
        free = raw.get("free", {})
        used = raw.get("used", {})

        for cur, total in spot.items():
            item = {
                "currency": cur,
                "total": total,
                "free": free.get(cur, 0),
                "used": used.get(cur, 0),
                "account_type": "spot",
            }
            normalized.append(item)

        # If exchange exposes other account types via 'info' or additional fields, adapters should
        # be extended to call those endpoints (not standardized by ccxt). For brevity, omitted here.

        return normalized
