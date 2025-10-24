from typing import Dict, Any, Optional
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
            "default": {
                "name": self.exchange_id,
                "options": None
            }
        }
        self.demo = False
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
        for key, profile in self.connectors.items():
            name = profile.get("name")
            options = profile.get("options") or {}
            connector_class = getattr(ccxt, name, None)

            if connector_class:
                ex_instance: Exchange = connector_class(params)
                for option, value in options.items():
                    ex_instance.options[option] = value

                instances[key] = ex_instance

                if self.testnet:
                    ex_instance.set_sandbox_mode(True)
                
                if self.demo:
                    ex_instance.enable_demo_trading(True)

        return instances

    async def _close(self):
        for ex in self.exchanges.values():
            try:
                await ex.close()
            except Exception:
                pass
        self.exchanges.clear()

    async def fetch_balance(self, params={}) -> Dict[str, Any]:
        exchange = self.exchanges.get("balance") or self.exchanges.get("default")
        fetch_method = getattr(exchange, "fetch_balance")
        if not fetch_method:
            logger.info(f"Exchange {self.exchange_id} does not have fetch_balance() method")
            return None
        
        try:
            balances = await fetch_method(params=params)
            if not balances:
                return balances

            non_empty_balances = {
                symbol: balance
                for symbol, balance in balances.items()
                if isinstance(balance, dict) and balance.get('total', 0) > 0
            }

            return non_empty_balances

        except Exception as e:
            logger.error(f"fetch_balance() error: {e}")
            return None

    async def fetch_positions(self, params={}) -> Dict[str, Any]:
        exchange = self.exchanges.get("positions") or self.exchanges.get("default")
        fetch_method = getattr(exchange, "fetch_positions")
        if not fetch_method:
            logger.info(f"Exchange {self.exchange_id} does not have fetch_positions() method")
            return None
        
        try:
            return await fetch_method(params=params)
        except Exception as e:
            logger.error(f"fetch_positions() error: {e}")
            return None
        
    async def fetch_options_positions(self, params={}) -> Dict[str, Any]:
        exchange = self.exchanges.get("options") or self.exchanges.get("default")
        fetch_method = getattr(exchange, "fetch_option_positions")
        if not fetch_method:
            logger.info(f"Exchange {self.exchange_id} does not have fetch_option_positions() method")
            return None
        
        try:
            return await fetch_method(params=params)
        except Exception as e:
            logger.error(f"fetch_options_balance() error: {e}")
            return None

    async def fetch_earn_balance(self) -> Dict[str, Any]:
        logger.error("fetch_earn_balance() not implemented")
        return None

    async def fetch_funding_fees(self) -> Dict[str, Any]:
        exchange = self.exchanges.get("funding_fee") or self.exchanges.get("default")
        fetch_method = getattr(exchange, "fetch_funding_history")

        if not fetch_method:
            logger.info(f"Exchange {self.exchange_id} does not have fetch_funding_history() method")
            return None
        
        try:
            return await fetch_method()
        except Exception as e:
            logger.error(f"fetch_funding_fees() error: {e}")
            return None
