from typing import Dict, Any, List, Optional
import asyncio
import ccxt.pro as ccxt
from app.ccxt.base import BaseAdapter
from app.utils.logging import get_logger


logger = get_logger("ccxt_bybit_adapter")


class BybitAdapter(BaseAdapter):
    def __init__(self, exchange_id: str, credentials: Optional[dict[str, str]] = None):
        super().__init__(exchange_id, credentials)
    
    async def fetch_earn_balance(self) -> List[Dict[str, Any]]:
        exchange: ccxt.bybit = self.exchanges.get("default")
        try:
            responses = await asyncio.gather(
                exchange.private_get_v5_earn_position(params={"category": "FlexibleSaving"}),
                exchange.private_get_v5_earn_position(params={"category": "OnChain"}),
                return_exceptions=True
            )

            earn_positions: List[Dict[str, Any]] = []
            for response in responses:
                result = response["result"]
                if not result:
                    logger.info("No result")
                    continue
                
                positions = result["list"]
                if not isinstance(positions, list):
                    logger.info("No list")
                    continue

                if len(positions) == 0:
                    logger.info("Empty list")
                    continue
                
                earn_positions.extend(list)

        except Exception as e:
            logger.error(f"fetch_earn_balance() error: {e}")
            return []
