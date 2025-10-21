from typing import Dict, Optional

# Hard-coded for demo. Replace with actual credentials service
credentials = {
    "nitoy-deribit": {
        "exchange": "deribit",
        "credentials": {"apiKey": "S7rgcsDs", "secret": "yEv8rojgtHv2es404_OM2gzWrIa3ZQPgKfzBJs-wqzg"},
    }
}


async def get_credentials_for_account(account_id: str) -> Optional[Dict[str, str]]:
    return credentials.get(account_id)
