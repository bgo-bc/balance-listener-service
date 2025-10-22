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

        balance = await self.fetch_balance()
        if balance:
            balances.append({
                "category": "balance",
                "data": balance
            })

        earn = await self.fetch_earn_balance()
        if earn:
            balances.append({
                "category": "earn",
                "data": earn
            })

        positions = await self.fetch_positions()
        if positions:
            balances.append({
                "category": "positions",
                "data": positions
            })

        options = await self.fetch_options_balance()
        if options:
            balances.append({
                "category": "options",
                "data": options
            })

        return balances

    async def fetch_balance(self) -> Dict[str, Any]:
        exchange = self.exchanges.get("balance") or self.exchanges.get("default")
        balance = await exchange.fetch_balance()
        return balance

    async def fetch_positions(self) -> Dict[str, Any]:
        exchange = self.exchanges.get("positions") or self.exchanges.get("default")
        positions = await exchange.fetch_positions()
        return positions

    async def fetch_options_balance(self) -> Dict[str, Any]:
        return None

    async def fetch_earn_balance(self) -> Dict[str, Any]:
        return None

    async def fetch_funding_fees(self) -> List[Dict[str, Any]]:
        # self.exchange.fetch_funding_rate_history()
        return []
