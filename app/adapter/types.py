from pydantic import BaseModel, Field
from typing import Any, Dict, Protocol

class EndpointConfig(BaseModel):
    path: str
    params: Dict[str, Any] = Field(default_factory=dict)
    requires_auth: bool = False
    translation: Dict[str, Any] = Field(default_factory=dict) # not yet supported

class AdapterConfig(BaseModel):
    exchange: str
    endpoints: Dict[str, EndpointConfig] = Field(default_factory=dict)

class Adapter(Protocol):
    async def fetch(self, entity_name: str, **kwargs) -> Dict[str, Any]: ...
    def sign(self, endpoint: EndpointConfig, params: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, str]]: ...
    def register_endpoint(self, name: str, config: EndpointConfig) -> None: ...
    def with_credentials(self, api_key: str, api_secret: str): ...
