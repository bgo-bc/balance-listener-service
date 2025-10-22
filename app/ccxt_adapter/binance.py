from typing import Dict, Any, List, Optional
from ccxt.base.exchange import Exchange
import ccxt.async_support as ccxt
from app.ccxt_adapter.base import BaseAdapter
from app.utils.logging import get_logger

logger = get_logger("ccxt_binance_adapter")


class BinanceAdapter(BaseAdapter):
    def __init__(self, exchange_id: str, credentials: Optional[dict[str, str]] = None):
        super().__init__(exchange_id, credentials)
        self.connectors = {
            "default": self.exchange_id,
            "balance": "binance",
            "options": "binance",
            "positions": "binanceusdm",
        }


