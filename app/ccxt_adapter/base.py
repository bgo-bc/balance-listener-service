from typing import Dict, Any, List, Optional
from ccxt.base.exchange import Exchange
import ccxt.async_support as ccxt
from app.utils.logging import get_logger


logger = get_logger("ccxt_adapter")


class BaseAdapter:
    def __init__(self, exchange_id: str, credentials: Optional[dict[str, str]] = None):
        self.exchange_id = exchange_id.lower()
        self.credentials = credentials or {}
        self.exchanges: Dict[str, Exchange] = {}
        self.connectors = {
            "default": self.exchange_id
        }
        self.testnet = True

    async def __aenter__(self):
        await self._init_exchanges()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._close()

    async def _init_exchanges(self):
        self.exchanges = await self.create_instances(self.credentials)
        logger.info(f"Initialized {self.exchange_id} with {list(self.exchanges.keys())}")

    async def create_instances(self, credentials: dict) -> Dict[str, Exchange]:
        params = {
            "enableRateLimit": True,
            "apiKey": credentials.get("apiKey"),
            "secret": credentials.get("secret"),
        }
        instances = {}
        for key, ccxt_name in self.connectors.items():
            ex_class = getattr(ccxt, ccxt_name, None)
            if ex_class:
                ex_instance: Exchange = ex_class(params)
                instances[key] = ex_instance

                if self.testnet:
                    ex_instance.set_sandbox_mode(True)

        return instances

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

    async def fetch_balance(self, params={}) -> Dict[str, Any]:
        exchange = self.exchanges.get("balance") or self.exchanges.get("default")
        fetch_method = getattr(exchange, "fetch_balance")
        if not fetch_method:
            return None
        
        return await fetch_method(params=params)

    async def fetch_positions(self, params={}) -> Dict[str, Any]:
        exchange = self.exchanges.get("positions") or self.exchanges.get("default")
        fetch_method = getattr(exchange, "fetch_positions")
        if not fetch_method:
            return None
        
        return await fetch_method(params=params)

    async def fetch_options_balance(self, params={}) -> Dict[str, Any]:
        exchange = self.exchanges.get("options") or self.exchanges.get("default")
        fetch_method = getattr(exchange, "fetch_option_positions")
        if not fetch_method:
            return None
        
        return await fetch_method(params=params)

    async def fetch_earn_balance(self) -> Dict[str, Any]:
        return None

    async def fetch_funding_fees(self) -> List[Dict[str, Any]]:
        return None
