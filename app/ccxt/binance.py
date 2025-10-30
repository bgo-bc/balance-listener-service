from typing import Dict, Any, List, Optional
import ccxt.async_support as ccxt
from app.ccxt.base import BaseAdapter
from app.utils.logging import get_logger

logger = get_logger("ccxt_binance_adapter")

class BinanceAdapter(BaseAdapter):
    def __init__(self, exchange_id: str, credentials: Optional[dict[str, str]] = None):
        super().__init__(exchange_id, credentials)
        self.testnet = False
        self.demo = True
        self.connectors = {
            "default": {
                "name": "binance"
            },
            "balance": {
                "name": "binance",
                # "options": {
                #     "defaultType": "spot"
                # }
            },
            # "options": {
            #     "name": "binance",
            #     "options": {
            #         "defaultType": "option"
            #     }
            # },
            "positions": {
                "name": "binanceusdm",
                # "options": {
                #     "defaultType": "future"
                # }
            },
            "positions-inverse": {
                "name": "binancecoinm",
                # "options": {
                #     "defaultType": "delivery"
                # }
            }
        }

    async def fetch_earn_balance(self) -> List[Dict[str, Any]]:
        exchange: ccxt.binance = self.exchanges.get("default")
        try:
            flexible = await exchange.sapi_get_simple_earn_flexible_position()
            locked = await exchange.sapi_get_simple_earn_locked_position()

            return [flexible, locked]
        except Exception as e:
            logger.error(f"fetch_earn_balance() error: {e}")
            return None
