from app.credentials import get_credentials_for_account
from app.ccxt.adapter import CCXTAdapter
from app.utils.logging import get_logger

logger = get_logger("task_processor")


class TaskProcessor:
    async def process(self, task: dict):
        account_id = task.get("account_id")
        fetch_type = task.get("type", "balances")

        creds_info = await get_credentials_for_account(account_id)
        if not creds_info:
            logger.warning(f"No credentials for {account_id}, skipping")
            return

        exchange = creds_info.get("exchange")
        credentials = creds_info.get("credentials")

        async with CCXTAdapter(exchange, credentials) as adapter:
            try:
                if fetch_type == "balances":
                    # Fetch all balances (spot, earn, futures, etc.)
                    all_balances = await adapter.fetch_balances()

                    if not all_balances:
                        logger.info(f"No balances for {exchange}:{account_id}")
                        return

                    # Publish each balance category
                    for balance in all_balances:
                        category = balance.get("category")
                        data = balance.get("data")

                        topic = f"{category}_balance.{exchange}.{account_id}"
                        await self._publish(topic, data)

                elif fetch_type == "funding_fees":
                    funding_fees = await adapter.fetch_funding_fees()
                    
                    if not funding_fees:
                        logger.info(f"No funding fees for {exchange}:{account_id}")
                        return
                    
                    topic = f"funding_fees.{exchange}.{account_id}"
                    await self._publish(topic, funding_fees)

                else:
                    logger.warning(f"Unknown fetch_type '{fetch_type}' for {account_id}")

            except Exception as e:
                logger.error(f"Processor error for {exchange}:{account_id} ({fetch_type}): {e}")

    async def _publish(self, topic: str, data):
        # TODO: Replace with NATS publish
        size = len(data) if isinstance(data, dict) else "?"
        logger.info(f"[PUBLISH] {topic} ({size} items)")
