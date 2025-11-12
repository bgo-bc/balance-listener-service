from typing import Dict
from app.adapter.types import Adapter, AdapterConfig
from app.adapter import exchanges

class AdapterRegistry:
    def __init__(self):
        self.adapters: Dict[str, Adapter] = {}
        self._init_adapters()

    def _init_adapters(self):
        for id in exchanges.exchange_ids:
            exchange_class = getattr(exchanges, id)
            exchange = exchange_class(id)

            self.adapters[id] = exchange

    def get_adapter(self, exchange: str, api_key: str, secret: str):
        return self.adapters.get(exchange).with_credentials(api_key, secret)

    def register_config(self, config: AdapterConfig):
        adapter: Adapter = self.adapters.get(config.exchange)
        if not adapter:
            raise ValueError(f"Exchange '{config.exchange}' not initialized.")
        
        for name, endpoint_config in config.endpoints.items():
            adapter.register_endpoint(name, endpoint_config)


# global registry instance
adapter_registry = AdapterRegistry()
