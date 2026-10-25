# Day 2 — HTTP, REST APIs and JSON

This project covers Day 2 of a backend and AI integrations learning plan. The goal is to understand how a Python program communicates with an external application through an HTTP API and works with the JSON response.

## What this project demonstrates

- Sending a `GET` request to the JSONPlaceholder users API with Python Requests.
- Checking the HTTP response status and handling request errors.
- Using a query parameter (`id`) to retrieve a specific user.
- Parsing the response as JSON and handling an unknown user ID.
- Displaying only the requested user's name and address fields.
- Transforming user records and saving the selected fields to `users.json`.

The learning plan also introduces the request-response cycle, HTTP methods, headers, query parameters, status codes, and JSON as a data-exchange format. This exercise specifically implements GET requests.

## Run the exercise

Install the dependency:

```bash
python -m pip install requests
```

Run the script from the project root:

```bash
python API_call.py
```

Choose an operation when prompted:

1. Search for a user by ID.
2. Transform and save all users' names and addresses to `users.json`.
3. Show all users returned by the data source.

The data source is [JSONPlaceholder](https://jsonplaceholder.typicode.com/users), a mock API for learning and testing.

## Project files

- `API_call.py` — fetches users, displays them, searches by ID, and transforms/saves the selected fields.
- `users.json` — sample output containing user names and address fields.
- `day_2/` — reserved for Day 2 materials added as the project grows.

New files and folders can be added to this repository over time. Git includes new files when they are staged (for example, with `git add -A`); empty folders need a placeholder file such as `.gitkeep` to be stored.
