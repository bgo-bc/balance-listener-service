from app.ccxt.base import BaseAdapter
from app.ccxt.binance import BinanceAdapter
from app.ccxt.deribit import DeribitAdapter

ADAPTERS = {
    "binance": BinanceAdapter,
    "deribit": DeribitAdapter,
}

async def get_adapter(exchange, credentials) -> BaseAdapter:
    adapter_cls = ADAPTERS.get(exchange, BaseAdapter)
    return adapter_cls(exchange, credentials)
