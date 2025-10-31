from typing import Dict, Optional

# Hard-coded for demo. Replace with actual credentials service
credentials = {
    "demo-deribit-account-123": {
        "exchange": "deribit",

        # https://test.deribit.com/account/BTC/api
        "credentials": {
            "apiKey": "", 
            "secret": ""
        },
    },
    "demo-binance-account-123": {
        "exchange": "binance", 

        # https://demo.binance.com/en/my/settings/api-management
        "credentials": {
            "apiKey": "",
            "secret": ""
        }
    }
}


async def get_credentials_for_account(account_id: str) -> Optional[Dict[str, str]]:
    return credentials.get(account_id)
