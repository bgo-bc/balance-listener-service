from typing import Dict, Any, List, Optional
from app.ccxt.base import BaseAdapter
from app.utils.logging import get_logger


logger = get_logger("ccxt_binance_adapter")


class DeribitAdapter(BaseAdapter):
    def __init__(self, exchange_id: str, credentials: Optional[dict[str, str]] = None):
        super().__init__(exchange_id, credentials)

    async def fetch_options_positions(self) -> List[Dict[str, Any]]:
        positions = await super().fetch_positions(params={
            "kind": "option"
        })
        return [positions]
    
    async def fetch_funding_fees(self) -> List[Dict[str, Any]]:
        exchange = self.exchanges.get("funding_fee") or self.exchanges.get("default")
        fetch_method = getattr(exchange, "fetch_funding_rate_history")
        
        if not fetch_method:
            logger.info(f"Exchange {self.exchange_id} does not have fetch_funding_rate_history() method")
            return None
        
        try:
            return [await fetch_method(symbol="BTC-PERPETUAL")]
        except Exception as e:
            logger.error(f"fetch_funding_fees() error: {e}")
            return None
