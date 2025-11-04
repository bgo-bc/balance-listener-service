from app.ccxt.base import BaseAdapter
from app.ccxt.binance import BinanceAdapter
from app.ccxt.deribit import DeribitAdapter
from app.ccxt.gateio import GateioAdapter

ADAPTERS = {
    "binance": BinanceAdapter,
    "deribit": DeribitAdapter,
    "gateio": GateioAdapter
}

async def get_adapter(exchange, credentials) -> BaseAdapter:
    adapter_cls = ADAPTERS.get(exchange, BaseAdapter)
    return adapter_cls(exchange, credentials)
