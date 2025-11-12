from typing import Any, Dict
from app.adapter.http_client import HttpClient
from app.adapter.types import EndpointConfig, Adapter
from app.utils.logging import get_logger

logger = get_logger("adapter")


class BaseAdapter(Adapter):
    def __init__(self, name: str):
        self.name: str = name
        self.api_key: str = None
        self.api_secret: str = None
        self.client: HttpClient = None
        self.endpoints: Dict[str, EndpointConfig] = {}

    def with_credentials(self, api_key: str, api_secret: str):
        cls = type(self)
        instance = cls(name=self.name)
        instance.endpoints = self.endpoints  # shared endpoints
        instance.client = HttpClient()       # fresh client
        instance.api_key = api_key
        instance.api_secret = api_secret
        return instance

    def register_endpoint(self, name: str, config: EndpointConfig):
        self.endpoints[name] = config

    def get_endpoint(self, name: str) -> EndpointConfig:
        if name not in self.endpoints:
            raise ValueError(f"Endpoint '{name}' not registered for {self.name}")
        return self.endpoints[name]

    async def fetch(self, entity_name: str, **kwargs) -> Dict[str, Any]:
        endpoint_config = self.get_endpoint(entity_name)
        params = {**endpoint_config.params, **kwargs}

        headers = {}
        if endpoint_config.requires_auth:
            params, headers = self.sign(endpoint_config, params)

        return await self.client.fetch(endpoint_config.path, params=params, headers=headers)

    def sign(self, endpoint: EndpointConfig, params: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, str]]:
        # Override in subclasses
        raise Exception(self.name + ' sign() is not implemented')
    