# In-memory registry of accounts that are polling periodically via api
# For production, this can be persisted (DB) and driven by durable queue
POLLING_ACCOUNTS: dict[str, dict] = {}

# In-memory registry of accounts that are streaming via websocket
# For production, this can be persisted (DB) and driven by durable queue
STREAMING_ACCOUNTS: dict[str, dict] = {}
