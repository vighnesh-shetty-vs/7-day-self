# Day 7 — AI Support Ticket Integration

## What this builds

A small, offline-first capstone that demonstrates a reusable data connector,
validated backend endpoints, a deterministic AI-style classification workflow,
an authenticated webhook, and automated tests.

## Project structure

- `tickets.json` — local sample-ticket data source; no external API is needed.
- `ticket_connector.py` — reads the source, validates every record, and exposes
  ticket lookup methods. Source failures are raised as `TicketSourceError`.
- `workflow.py` — classifies tickets into `billing`, `technical`, or
  `account-related` using keyword rules. Billing keywords take priority,
  followed by account keywords; unmatched messages default to technical.
- `app.py` — FastAPI service with search, category filtering, ticket lookup,
  health check, and a bearer-authenticated, idempotent webhook example.
- `test_ticket_connector.py` and `test_app.py` — offline tests for success,
  invalid data and inputs, source failures, and webhook behavior.

## Setup

From the repository root, create and activate a virtual environment, then
install this day's dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r day_7\requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install -r day_7/requirements.txt
```

## Run the service

From the repository root:

```bash
uvicorn day_7.app:app --reload
```

Interactive API documentation is available at <http://127.0.0.1:8000/docs>.

Examples:

```text
GET http://127.0.0.1:8000/health
GET http://127.0.0.1:8000/tickets
GET http://127.0.0.1:8000/tickets?q=refund
GET http://127.0.0.1:8000/tickets?category=billing
GET http://127.0.0.1:8000/tickets/1001
```

Successful ticket responses include the validated source fields and the
classification category. Unknown IDs return `404`; invalid query/path values
return FastAPI's `422` validation response; unreadable or malformed source data
returns a consistent `500` detail response.

## Webhook example

Configure a shared bearer token before starting the service:

```powershell
$env:WEBHOOK_BEARER_TOKEN = "replace-with-a-local-demo-token"
```

Send a ticket-created event:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/webhooks/tickets `
  -Headers @{ Authorization = "Bearer replace-with-a-local-demo-token" } `
  -ContentType "application/json" `
  -Body '{"event_id":"evt_demo_001","event_type":"ticket.created","ticket_id":1001}'
```

The endpoint returns `202` for an accepted event, `401` for invalid
authentication, `503` if authentication has not been configured, `409` for a
duplicate event ID, and `422` for an invalid payload. Event IDs are kept in
process memory for this demonstration, not in durable storage.

## Run tests

From the repository root:

```bash
python -m pytest day_7 -q
```

All tests use the local fixture or temporary files; they do not depend on
network access or a running server.

## 3–5 minute demo outline

1. **0:00–0:45 — Architecture:** show `tickets.json`, explain that
   `TicketConnector` isolates the source and validates each record.
2. **0:45–1:45 — API:** run Uvicorn, open `/docs`, search for `refund`, filter
   by `billing`, and retrieve ticket `1001`.
3. **1:45–2:30 — Workflow:** open `workflow.py` and explain deterministic
   keyword rules and the billing/account/technical categories.
4. **2:30–3:30 — Webhook and errors:** submit the authenticated example, then
   describe duplicate, unauthorized, invalid-input, and missing-ticket
   responses.
5. **3:30–4:30 — Tests and limitations:** run pytest and explain that this is a
   rule-based local demo, not an LLM or production integration.

## Limitations and production next steps

- Classification is a transparent keyword heuristic, not an LLM, and can
  misclassify ambiguous messages.
- Tickets are read from a local JSON file; there is no live vendor API,
  database, pagination, or retry policy.
- Webhook deduplication is in-memory and resets on process restart; production
  needs durable idempotency storage, secret rotation, and delivery monitoring.
- The webhook acknowledges events but does not mutate ticket records or
  enqueue background work.
- Authentication, authorization, rate limiting, structured logging, and
  deployment configuration need production-grade implementations.
