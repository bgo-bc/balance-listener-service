from typing import Dict, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.utils.queue import TaskQueue
from app.type_defs import FetchTask
from app.utils.logging import get_logger

logger = get_logger("task_scheduler")


class TaskScheduler:
    def __init__(self, listening_accounts: Dict[str, dict], queue: TaskQueue):
        self.listening_accounts = listening_accounts
        self.queue = queue
        self.scheduler = AsyncIOScheduler()

    async def enqueue_account(self, account_id: str, types: List[str]):
        try:
            task = FetchTask(account_id=account_id, types=types)
            logger.info(f"Enqueueing {type} balance task for account {account_id}")
            await self.queue.put(task.model_dump())
        except Exception as e:
            logger.error(f"Failed to enqueue account {account_id}: {e}")

    async def enqueue_all_accounts(self, types: List[str]):
        if not self.listening_accounts:
            logger.debug(f"No accounts to enqueue for frequency={type}")
            return

        for account_id in list(self.listening_accounts.keys()):
            await self.enqueue_account(account_id, types)

    async def _balance_check_job(self):
        await self.enqueue_all_accounts(["balance", "earn_balance", "positions", "option_positions"])

    async def _funding_fee_check_job(self):
        await self.enqueue_all_accounts(["funding_fees"])

    async def start(self):
        if self.scheduler.running:
            logger.warning("Scheduler already running")
            return

        # Schedule periodic jobs
        self.scheduler.add_job(
            self._balance_check_job,
            IntervalTrigger(seconds=30),
            id="balance_check_job",
            coalesce=True,
            max_instances=1,
            misfire_grace_time=15,
        )
        self.scheduler.add_job(
            self._funding_fee_check_job,
            IntervalTrigger(hours=8),
            id="funding_fee_check_job",
            coalesce=True,
            max_instances=1,
            misfire_grace_time=60,
        )

        self.scheduler.start()
        logger.info("Scheduler started with 30s and 8h intervals")

    async def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")
