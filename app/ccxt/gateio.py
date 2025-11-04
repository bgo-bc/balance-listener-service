from typing import Dict, Any, List, Optional
import ccxt.pro as ccxt
from app.ccxt.base import BaseAdapter
from app.utils.logging import get_logger


logger = get_logger("ccxt_binance_adapter")


class GateioAdapter(BaseAdapter):
    def __init__(self, exchange_id: str, credentials: Optional[dict[str, str]] = None):
        super().__init__(exchange_id, credentials)
    
    async def fetch_funding_fees(self) -> List[Dict[str, Any]]:
        exchange: ccxt.gateio = self.exchanges.get("funding_fees") or self.exchanges.get("default")
        fetch_method = getattr(exchange, "fetch_funding_history")

        if not fetch_method:
            logger.info(f"Exchange {self.exchange_id} does not have fetch_funding_history() method")
            return []
        
        try:
            return [await fetch_method(
                params={"type": "future"}
            )]
        except Exception as e:
            logger.error(f"fetch_funding_fees() error: {e}")
            return []
