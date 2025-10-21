from typing import Dict, Any, List, Optional
from ccxt.base.exchange import Exchange
import ccxt.async_support as ccxt

from app.ccxt.profiles import ExchangeProfile, EXCHANGE_PROFILES
from app.utils.logging import get_logger


logger = get_logger("ccxt_adapter")


class CCXTAdapter:
    def __init__(self, exchange_id: str, credentials: Optional[dict[str, str]] = None):
        self.exchange_id = exchange_id.lower()
        self.credentials = credentials or {}
        self.exchanges: Dict[str, Exchange] = {}
        self.profile: Optional[ExchangeProfile] = None

    async def __aenter__(self):
        await self._init_exchanges()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._close()

    async def _init_exchanges(self):
        self.profile = EXCHANGE_PROFILES.get(self.exchange_id)
        if not self.profile:
            raise ValueError(f"Unsupported exchange id: {self.exchange_id}")

        self.exchanges = await self.profile.create_instances(self.credentials)
        logger.info(f"Initialized {self.exchange_id} with {list(self.exchanges.keys())}")

    async def _close(self):
        for ex in self.exchanges.values():
            try:
                await ex.close()
            except Exception:
                pass
        self.exchanges.clear()

    async def fetch_balances(self) -> List[Dict[str, Any]]:
        balances = []

        # spot
        spot = self.exchanges.get("spot") or self.exchanges.get("default")
        spot_balance = await spot.fetch_balance()

        balances.append({
            "category": "spot",
            "data": spot_balance
        })

        # TODO: fetch earn balance and append to 'balances'

        # TODO: fetch positions balance and append to 'balances'

        # TODO: fetch options balance and append to 'balances'

        return balances


    async def fetch_funding_fees(self) -> List[Dict[str, Any]]:
        # self.exchange.fetch_funding_rate_history()
        return []
