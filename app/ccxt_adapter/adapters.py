from app.ccxt_adapter.base import BaseAdapter
from app.ccxt_adapter.binance import BinanceAdapter
from app.ccxt_adapter.deribit import DeribitAdapter

ADAPTERS = {
    "binance": BinanceAdapter,
    "deribit": DeribitAdapter,
}

async def get_adapter(exchange, credentials) -> BaseAdapter:
    adapter_cls = ADAPTERS.get(exchange, BaseAdapter)
    return adapter_cls(exchange, credentials)
