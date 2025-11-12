# Balance Listener Service

The **Balance Listener Service** is a modular Python application designed to aggregate and normalize cryptocurrency account balances across multiple exchanges.  

---

## 🚀 Overview

The service performs the following tasks:

- Connects to configured exchange(s) via secure API credentials  
- Retrieves user balances across multiple account types (spot, earn, funding, etc.)  
- Normalizes the balance data into a consistent format  
- Forwards or stores the results for reconciliation and reporting

Balances are fetched periodically by a scheduler. Accounts to be monitored are registered via an API endpoint.

---

## 🧩 Architecture Highlights

- **FastAPI** — provides an HTTP interface for manual balance trigger requests  
- **Async In-Memory Queue** — holds pending balance-fetch tasks (replaceable with Redis, NATS, or Celery in future)  
- **Scheduler** — periodically enqueues balance fetch tasks for registered accounts  
- **Worker(s)** — consume tasks from the queue and perform the actual balance retrieval  
- **Meta Adapter** — exchange abstraction layer that can be configured dynamically (e.g. url endpoints, response translation)

---

## ⚡ Quick Start Guide

### 🚀 Starting the Balance Listener Service

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app
```

Once the service is running, open your browser to:
👉 [http://localhost:8000/docs](http://localhost:8000/docs)

From there, you can configure each exchange adapter's configuration in the ```/configs/adapters``` endpoint:  
```
{
  "exchange": "binance",
  "endpoints": {
    "balance": {
      "path": "https://demo-api.binance.com/api/v3/account",
      "params": {},
      "requires_auth": true,
      "translation": {} # not yet supported
    }
  }
}
```

Then, you can **register an account** in the ```/listeners``` endpoint to start listening for balance updates.
```
{
  "account_id": "demo-binance-account-123"
}
```

---

### 📡 Listening to NATS Topics (Optional)

If you have NATS installed and running, you can subscribe to the balance updates published by the service.

#### Example: Subscribe to all Deribit balance updates
```bash
nats sub "balance.deribit.*"
```

#### Example: Subscribe to all exchanges’ balances
```bash
nats sub "balance.>"
```

#### Example: Subscribe to specific data categories
```bash
nats sub "positions.binance.*"
nats sub "funding_fees.deribit.*"
```

Each message will contain the **normalized balance or funding data** in JSON format.

---

💡 *Tip:*  
You can use `nats --server nats://localhost:4222` if your NATS server isn’t running on the default endpoint.

