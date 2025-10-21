from typing import Dict
from ccxt.base.exchange import Exchange
import ccxt.async_support as ccxt


class ExchangeProfile:
    def __init__(self, markets: Dict[str, str]):
        self.markets = markets  # e.g. {"spot": "binance", "usdm": "binanceusdm"}

    async def create_instances(self, credentials: dict) -> Dict[str, Exchange]:
        params = {
            "enableRateLimit": True,
            "apiKey": credentials.get("apiKey"),
            "secret": credentials.get("secret"),
        }
        instances = {}
        for key, ccxt_name in self.markets.items():
            ex_class = getattr(ccxt, ccxt_name, None)
            if ex_class:
                ex_instance: Exchange = ex_class(params)
                ex_instance.set_sandbox_mode(True)
                instances[key] = ex_instance

        return instances


EXCHANGE_PROFILES: Dict[str, ExchangeProfile] = {
    "binance": ExchangeProfile({
        "spot": "binance",
        "options": "binance",
        "futures": "binanceusdm",
    }),
    "deribit": ExchangeProfile({
        "default": "deribit",
    })
}
