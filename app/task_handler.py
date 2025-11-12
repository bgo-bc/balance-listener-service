import asyncio
from typing import Dict, List, Union
from app.credentials import get_credentials_for_account
from app.adapter import adapter_registry
from app.adapter.types import Adapter
from app.utils.logging import get_logger
from app.types import TaskProcessor
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
        # Only balance is supported for now
        fetch_types = ["balance"] # task.get("types", ["balance"])

        creds_info = await get_credentials_for_account(account_id)
        if not creds_info:
            logger.warning(f"No credentials for {account_id}, skipping")
            return

        exchange = creds_info.get("exchange")
        api_key = creds_info.get("api_key")
        secret = creds_info.get("secret")

        adapter: Adapter = adapter_registry.get_adapter(exchange, api_key, secret)
        if not adapter:
            logger.warning(f"Adapter for {exchange} not found")
            return
        
        try:
            async def fetch_and_publish(entity_type: str):
                try:
                    logger.info(f"Fetching {entity_type} for {account_id}")
                    data = await adapter.fetch(entity_type)
                    if not data:
                        logger.info(f"No {entity_type} data fetched  for {account_id}")
                        return
                    
                    topic = f"{entity_type}.{exchange}.{account_id}"
                    logger.info(f"Publishing {entity_type} data for {account_id}")
                    await self._publish(topic, data)
                except asyncio.CancelledError:
                    logger.info(f"Cancelled fetch for {entity_type}:{account_id}")
                    raise
                except Exception as e:
                    logger.warning(f"Error fetching {entity_type} for {account_id}: {e}")

            # Fetch and publish in parallel
            tasks = [
                asyncio.create_task(fetch_and_publish(fetch_type))
                for fetch_type in fetch_types
            ]

            # Wait for all to finish concurrently
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception:
            pass

    async def _publish(self, topic: str, data: Union[List[Dict], Dict]):
        payloads = data if isinstance(data, list) else [data]
        await asyncio.gather(*[
            nats_publisher.publish(topic, payload)
            for payload in payloads
        ])
