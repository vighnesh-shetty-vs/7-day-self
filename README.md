# Backend and AI Integrations Learning Project

This repository contains hands-on exercises for preparing for backend and AI integrations work at StackMint. The project follows a practical learning approach: understand a concept, write code, test it, handle failures, and document what was built.

The learning plan covers API integration, backend services, reusable connectors, testing, webhooks, OAuth, AI tool calling, MCP, and a final integration project. This repository is being developed for **Days 2, 4, 5, 6, and 7**; it does not include a Day 3 exercise.

## Current project contents

- [`day_2/`](./day_2/) — HTTP, REST APIs, Requests, and JSON.
- [`day_4/`](./day_4/) — a reusable CRM connector with request and response validation.

Folders for the remaining selected days can be added as those activities are completed.

## Prerequisites

- Python 3
- `pip`
- Internet access for the JSONPlaceholder API exercises

Install the dependency used by the current exercises:

```bash
python -m pip install requests
```

## Run the exercises

From the repository root, open a terminal in `day_2` and run:

```bash
cd day_2
python API_call.py
```

In a separate terminal from the repository root, run the Day 4 connector:

```bash
cd day_4
python crm_connector.py
```

The Day 2 program prompts you to choose whether to search for a user by ID, save users' names and addresses to JSON, or display all users. The Day 4 program retrieves a customer record from JSONPlaceholder and reports network, HTTP, or response-validation errors.

## Growing the repository

Add new work in the matching day folder, for example `day_5/` or `day_6/`. Git tracks files rather than empty directories, so put a file such as `README.md` or `.gitkeep` in a new folder.

To stage new and updated files, then commit and push them:

```bash
git add -A
git commit -m "Describe the completed work"
git push
```

See each day folder's README for its objective and activities.
