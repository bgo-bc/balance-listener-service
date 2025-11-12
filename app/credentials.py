from typing import Dict, Optional

# Hard-coded for demo. Replace with actual credentials service
credentials = {
    "demo-deribit-account-123": {
        "exchange": "deribit",

        # https://test.deribit.com/account/BTC/api
        "api_key": "", 
        "secret": ""
    },
    "demo-binance-account-123": {
        "exchange": "binance", 

        # https://demo.binance.com/en/my/settings/api-management
        "api_key": "",
        "secret": ""
    },
    "demo-gateio-account-123": {
        "exchange": "gateio",

        # https://testnet.gate.com/myaccount/profile/api-key/save
        "api_key": "",
        "secret": ""
    },
    "demo-bybit-account-123": {
        "exchange": "bybit",

        # https://testnet.bybit.com/app/user/api-management
        "api_key": "",
        "secret": ""
    }
}


async def get_credentials_for_account(account_id: str) -> Optional[Dict[str, str]]:
    return credentials.get(account_id)
