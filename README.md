# Balance Listener Service

The **Balance Listener Service** is a modular Python application designed to aggregate and normalize cryptocurrency account balances across multiple exchanges using [ccxt](https://github.com/ccxt/ccxt).  
It is structured as a monolithic app for now but architected to support distributed deployment in the future.

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
- **Exchange Adapter** — a thin abstraction over `ccxt` to handle multiple exchanges consistently

This structure allows easy migration from a single-process design to a distributed microservice setup later.

---
