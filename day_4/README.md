# Day 4 — Build a Reusable Backend Connector

## Objective

Build a reusable connector module that communicates with an external application and hides request-handling details from the code that uses it.

## Activities

1. Design a connector interface around customer operations such as retrieving a customer by ID.
2. Implement `CRMConnector` in `crm_connector.py` using Python Requests and JSONPlaceholder.
3. Add request timeouts and handle network and HTTP errors.
4. Validate the API response: check that it is valid JSON and contains the expected customer ID, name, and email fields.
5. Handle malformed or missing response data with a clear validation error.
6. Consider optional bearer-token authentication, and distinguish an existing access token from a complete OAuth authorization flow.
7. Research pagination and rate limiting, and document the connector's expected inputs, outputs, and errors.

## Run

Install Requests if needed, then run from this folder:

```bash
python -m pip install requests
python crm_connector.py
```

The current example retrieves customer ID `1` from JSONPlaceholder and prints the normalized customer data.

## Success criteria

The connector is a separate, reusable Python module, and its request flow, response validation, and failure handling are clear. This is a learning prototype, not a production-ready enterprise connector.
