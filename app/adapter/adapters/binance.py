import time
import hmac
import hashlib
from urllib.parse import urlencode
from app.adapter.base_adapter import BaseAdapter
from app.utils.logging import get_logger


logger = get_logger("binance")


class binance(BaseAdapter):
    def sign(self, endpoint, params):
        logger.info("Signing!")

        params["timestamp"] = int(time.time() * 1000)
        query = urlencode(params)
        signature = hmac.new(self.api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
        params["signature"] = signature
        headers = {"X-MBX-APIKEY": self.api_key}

        return params, headers
