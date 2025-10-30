import asyncio
from typing import Dict
from app.nats_publisher import nats_publisher
from app.ccxt.adapters import get_adapter, BaseAdapter
from app.credentials import get_credentials_for_account
from app.account_registry import STREAMING_ACCOUNTS
from app.utils.logging import get_logger

logger = get_logger("ws_handler")


class WebsocketHandler:
    def __init__(self):
        # account_id -> asyncio.Task
        self.listening_accounts: Dict[str, asyncio.Task] = {}
        self.listening = True

    async def _watch_stream(self, adapter: BaseAdapter, account_id: str, exchange_id: str, stream_type: str):
        topic_prefix = f"{stream_type}_ws.{exchange_id}.{account_id}"

        while self.listening and account_id in self.listening_accounts:
            try:
                data = None

                if stream_type == "balance":
                    data = await asyncio.wait_for(adapter.watch_balance(), timeout=60.0)
                elif stream_type == "positions":
                    data = await asyncio.wait_for(adapter.watch_positions(), timeout=60.0)
                else:
                    logger.warning(f"Unknown stream type: {stream_type}")
                    return

                if not data:
                    continue
                
                await nats_publisher.publish(topic_prefix, data)

            except asyncio.TimeoutError:
                logger.warning(f"No {stream_type} updates for {exchange_id}:{account_id} in 60s.")
                continue
            except Exception as e:
                logger.error(f"WebSocket error ({stream_type}) for {exchange_id}:{account_id}: {e}")
                await asyncio.sleep(5)

    async def _account_runner(self, account_id):
        creds_info = await get_credentials_for_account(account_id)
        exchange_id = creds_info.get("exchange")
        credentials = creds_info.get("credentials")

        exchange_adapter = await get_adapter(exchange_id, credentials)

        async with exchange_adapter as adapter:
            logger.info(f"Started websocket listener for {exchange_id}:{account_id}")

            # Run multiple watchers concurrently using the same adapter
            watchers = [
                asyncio.create_task(self._watch_stream(adapter, account_id, exchange_id, "balance")),
                asyncio.create_task(self._watch_stream(adapter, account_id, exchange_id, "positions")),
            ]

            done, pending = await asyncio.wait(watchers, return_when=asyncio.FIRST_EXCEPTION)

            # Cancel any remaining watchers
            for task in pending:
                task.cancel()

            logger.info(f"Stopped websocket listener for {exchange_id}:{account_id}")

    async def watch_account(self, account_id: str):
        if account_id in self.listening_accounts:
            logger.warning(f"Already streaming for account[{account_id}]")
            return

        task = asyncio.create_task(self._account_runner(account_id))
        self.listening_accounts[account_id] = task
        logger.info(f"Added account[{account_id}] to websocket listening.")

    async def unwatch_account(self, account_id: str):
        task = self.listening_accounts.pop(account_id, None)
        if not task:
            logger.warning(f"Not listening for account[{account_id}]")
            return

        logger.info(f"Stopping websocket listener for account[{account_id}]...")
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        logger.info(f"Account[{account_id}] listener stopped.")

    async def start(self):
        for account_id in STREAMING_ACCOUNTS.keys():
            await self.watch_account(account_id)

    async def stop(self):
        logger.info("Stopping all websocket listeners...")
        self.listening = False

        for account_id, task in list(self.listening_accounts.items()):
            task.cancel()
            logger.info(f"Canceled task for account[{account_id}]")

        await asyncio.gather(*self.listening_accounts.values(), return_exceptions=True)
        self.listening_accounts.clear()
        logger.info("All websocket listeners stopped.")
