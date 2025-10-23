import json
import asyncio
from nats.aio.client import Client as NATS
from app.utils.logging import get_logger

logger = get_logger("nats")

class NatsPublisher:
    def __init__(self, nats_url="nats://0.0.0.0:4222"):
        self.nats_url = nats_url
        self.nc = NATS()
        self.connected = False
        self._connect_lock = asyncio.Lock()

    async def connect(self):
        async with self._connect_lock:
            if not self.connected:
                await self.nc.connect(self.nats_url)
                self.connected = True
                logger.info(f"Connected to {self.nats_url}")

    async def disconnect(self):
        if self.connected:
            await self.nc.drain()
            self.connected = False
            logger.info("Disconnected")

    async def publish(self, subject: str, data: dict):
        try:
            if not self.connected:
                await self.connect()

            payload = json.dumps(data).encode()
            await self.nc.publish(subject, payload)
            logger.info(f"Published message to subject: {subject}")

        except Exception as e:
            logger.warning(f"Failed to publish to {subject}: {e}")

nats_publisher = NatsPublisher()
