# Day 2 — HTTP, REST APIs and JSON

## Objective

Understand how a Python program communicates with another application through an HTTP API, and how to handle the JSON response.

## Activities

1. Learn the request-response cycle and the role of HTTP methods, headers, query parameters, status codes, and JSON.
2. Send a `GET` request to the JSONPlaceholder users endpoint using Python Requests.
3. Check the response status, set a timeout, and handle request errors.
4. Parse the response as JSON and use the `id` query parameter to search for a specific user.
5. Display only the name and address fields needed by the exercise.
6. Transform the user records and save the selected fields to `users.json`.
7. Try an unknown user ID and consider how the script behaves when the request fails.

## Run

From this folder:

```bash
python -m pip install requests
python API_call.py
```

Choose an operation from the menu. The saved `users.json` contains users' names and address fields only.

## Success criteria

- Retrieve data from an external API and parse its JSON response.
- Search by user ID and handle an ID that returns no matching user.
- Explain how HTTP status handling, timeouts, and request errors affect the result.
