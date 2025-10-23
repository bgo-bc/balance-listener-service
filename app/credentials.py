from typing import Dict, Optional

# Hard-coded for demo. Replace with actual credentials service
credentials = {
    "demo-deribit-account-123": {
        "exchange": "deribit",

        # https://test.deribit.com/account/BTC/api
        "credentials": {
            "apiKey": "S7rgcsDs", 
            "secret": "yEv8rojgtHv2es404_OM2gzWrIa3ZQPgKfzBJs-wqzg"
        },
    },
    "demo-binance-account-123": {
        "exchange": "binance", 

        # https://demo.binance.com/en/my/settings/api-management
        "credentials": {
            "apiKey": "2VGbmZjv4uUwk1Lma4b2KaMUkwGJIfrpOo1kO7igN2E3hxHCUjSlnZKpHr7ntumS",
            "secret": "p5hTk3JdXKmZ7fmxPdWuhYhCQa9oZd7uATPvuZ9286y1gj5jkc4QdjFvQgGgwYW8"
        }
    }
}


async def get_credentials_for_account(account_id: str) -> Optional[Dict[str, str]]:
    return credentials.get(account_id)
