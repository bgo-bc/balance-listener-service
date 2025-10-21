from app.credentials import get_credentials_for_account
from app.ccxt_adapter import CCXTAdapter
from app.utils.logging import get_logger

logger = get_logger("task_processor")


class TaskProcessor:
    async def process(self, task: dict):
        account_id = task.get("account_id")

        creds_info = await get_credentials_for_account(account_id)
        if not creds_info:
            logger.warning(f"No credentials for {account_id}, skipping")
            return

        exchange = creds_info.get("exchange")
        async with CCXTAdapter(exchange, creds_info.get("credentials")) as adapter:
            balances = await adapter.fetch_balances()

        logger.info(f"Fetched {len(balances)} assets for {account_id} on {exchange}")
        # TODO: Publish to NATS, DB, etc.
