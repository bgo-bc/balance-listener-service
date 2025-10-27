import asyncio
from typing import Dict, List, Union
from app.credentials import get_credentials_for_account
from app.ccxt.adapters import get_adapter
from app.utils.logging import get_logger
from app.type_defs import TaskProcessor
from app.nats_publisher import nats_publisher

logger = get_logger("task_handler")


class FetchTaskHandler(TaskProcessor):
    async def process(self, task: dict):
        try:
            await self.process_fetch_task(task)
        except asyncio.CancelledError:
            logger.warning("TaskProcessor cancelled during fetch task.")
            raise

    async def process_fetch_task(self, task: dict):
        account_id = task.get("account_id")
        fetch_types = task.get("types", ["balance"])

        creds_info = await get_credentials_for_account(account_id)
        if not creds_info:
            logger.warning(f"No credentials for {account_id}, skipping")
            return

        exchange = creds_info.get("exchange")
        credentials = creds_info.get("credentials")

        exchange_adapter = await get_adapter(exchange, credentials)
        async with exchange_adapter as adapter:
            fetch_map = {
                "balance": adapter.fetch_balance,
                "earn_balance": adapter.fetch_earn_balance,
                "positions": adapter.fetch_positions,
                "options": adapter.fetch_options_positions,
                "funding_fees": adapter.fetch_funding_fees,
            }

            async def fetch_and_publish(fetch_type: str, fetch_func):
                try:
                    logger.info(f"Fetching {fetch_type} for {account_id}")
                    data = await fetch_func()
                    if not data:
                        logger.info(f"No {fetch_type} data fetched  for {account_id}")
                        return
                    
                    topic = f"{fetch_type}.{exchange}.{account_id}"
                    logger.info(f"Publishing {fetch_type} data for {account_id}")
                    await self._publish(topic, data)
                except asyncio.CancelledError:
                    logger.info(f"Cancelled fetch for {fetch_type}:{account_id}")
                    raise
                except Exception as e:
                    logger.warning(f"Error fetching {fetch_type} for {account_id}: {e}")

            # Fetch and publish in parallel
            tasks = [
                asyncio.create_task(fetch_and_publish(fetch_type, fetch_func))
                for fetch_type, fetch_func in fetch_map.items()
                if fetch_type in fetch_types
            ]

            # Wait for all to finish concurrently
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _publish(self, topic: str, data: Union[List[Dict], Dict]):
        payloads = data if isinstance(data, list) else [data]
        await asyncio.gather(*[
            nats_publisher.publish(topic, payload)
            for payload in payloads
        ])
