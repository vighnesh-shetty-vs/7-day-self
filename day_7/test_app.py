import pytest
from fastapi.testclient import TestClient

from day_7.app import app, processed_event_ids

client = TestClient(app)
TOKEN = "test-webhook-token"


@pytest.fixture(autouse=True)
def reset_webhook_state(monkeypatch):
    processed_event_ids.clear()
    monkeypatch.setenv("WEBHOOK_BEARER_TOKEN", TOKEN)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_returns_consistent_ticket_shape_and_classification():
    response = client.get("/tickets", params={"q": "refund"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["tickets"][0] == {
        "id": 1001,
        "subject": "Refund for duplicate charge",
        "description": (
            "I was charged twice for my monthly subscription and need a refund."
        ),
        "customer_email": "maya@example.com",
        "status": "open",
        "category": "billing",
    }


@pytest.mark.parametrize(
    ("ticket_id", "expected_category"),
    [(1002, "account-related"), (1003, "technical"), (1005, "billing")],
)
def test_get_ticket_classifies_ticket(ticket_id, expected_category):
    response = client.get(f"/tickets/{ticket_id}")

    assert response.status_code == 200
    assert response.json()["category"] == expected_category


def test_category_filter_returns_only_matching_tickets():
    response = client.get("/tickets", params={"category": "account-related"})

    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert all(
        ticket["category"] == "account-related"
        for ticket in response.json()["tickets"]
    )


def test_get_ticket_returns_404_for_unknown_id():
    response = client.get("/tickets/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Ticket not found."}


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("/tickets/0", None),
        ("/tickets/not-an-id", None),
        ("/tickets", {"q": ""}),
        ("/tickets", {"category": "other"}),
    ],
)
def test_invalid_search_inputs_return_validation_errors(path, params):
    response = client.get(path, params=params)

    assert response.status_code == 422


def test_invalid_ticket_source_returns_explicit_server_error(monkeypatch):
    def fail_to_load():
        from day_7.ticket_connector import TicketSourceError

        raise TicketSourceError("source fixture failure")

    monkeypatch.setattr("day_7.app.connector.get_tickets", fail_to_load)

    response = client.get("/tickets")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Ticket source is unavailable or invalid."
    }


def test_webhook_accepts_valid_authenticated_event():
    response = client.post(
        "/webhooks/tickets",
        json={
            "event_id": "evt_001",
            "event_type": "ticket.created",
            "ticket_id": 1001,
        },
        headers={"Authorization": f"Bearer {TOKEN}"},
    )

    assert response.status_code == 202
    assert response.json() == {
        "received": True,
        "event_id": "evt_001",
        "ticket_id": 1001,
    }


@pytest.mark.parametrize("authorization", [None, "Bearer wrong", "Basic token"])
def test_webhook_rejects_invalid_authentication(authorization):
    headers = {}
    if authorization is not None:
        headers["Authorization"] = authorization

    response = client.post(
        "/webhooks/tickets",
        json={
            "event_id": "evt_002",
            "event_type": "ticket.created",
            "ticket_id": 1001,
        },
        headers=headers,
    )

    assert response.status_code == 401


def test_webhook_rejects_when_authentication_is_unconfigured(monkeypatch):
    monkeypatch.delenv("WEBHOOK_BEARER_TOKEN")

    response = client.post(
        "/webhooks/tickets",
        json={
            "event_id": "evt_003",
            "event_type": "ticket.created",
            "ticket_id": 1001,
        },
        headers={"Authorization": f"Bearer {TOKEN}"},
    )

    assert response.status_code == 503


@pytest.mark.parametrize(
    "payload",
    [
        {"event_id": "", "event_type": "ticket.created", "ticket_id": 1},
        {"event_id": "evt_004", "event_type": " ", "ticket_id": 1},
        {"event_id": "evt_004", "event_type": "ticket.created", "ticket_id": 0},
        {
            "event_id": "evt_004",
            "event_type": "ticket.created",
            "ticket_id": "1",
        },
        {
            "event_id": "evt_004",
            "event_type": "ticket.created",
            "ticket_id": 1,
            "unexpected": True,
        },
    ],
)
def test_webhook_rejects_invalid_payloads(payload):
    response = client.post(
        "/webhooks/tickets",
        json=payload,
        headers={"Authorization": f"Bearer {TOKEN}"},
    )

    assert response.status_code == 422


def test_webhook_rejects_duplicate_event():
    payload = {
        "event_id": "evt_duplicate",
        "event_type": "ticket.created",
        "ticket_id": 1001,
    }
    headers = {"Authorization": f"Bearer {TOKEN}"}

    first = client.post("/webhooks/tickets", json=payload, headers=headers)
    duplicate = client.post("/webhooks/tickets", json=payload, headers=headers)

    assert first.status_code == 202
    assert duplicate.status_code == 409
