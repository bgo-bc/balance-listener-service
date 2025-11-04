from typing import Dict, Any, List, Optional
import ccxt.pro as ccxt
from app.ccxt.base import BaseAdapter
from app.utils.logging import get_logger


logger = get_logger("ccxt_deribit_adapter")


class DeribitAdapter(BaseAdapter):
    def __init__(self, exchange_id: str, credentials: Optional[dict[str, str]] = None):
        super().__init__(exchange_id, credentials)

    async def fetch_options_positions(self) -> List[Dict[str, Any]]:
        positions = await super().fetch_positions(params={
            "kind": "option"
        })
        return [positions]
    
    async def fetch_funding_fees(self) -> List[Dict[str, Any]]:
        exchange: ccxt.deribit = self.exchanges.get("funding_fees") or self.exchanges.get("default")
        
        try:
            response = await exchange.private_get_get_settlement_history_by_currency(params={"currency": "BTC"})
            result = response["result"]
            return result["settlements"]
        except Exception as e:
            logger.error(f"fetch_funding_fees() error: {e}")
            return []
