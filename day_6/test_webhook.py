import pytest
from fastapi.testclient import TestClient

from day_6.webhook import app, event_ids

client = TestClient(app)
TOKEN = "test-webhook-token"
PAYLOAD = {
    "event_id": "evt_001",
    "event_type": "ticket.created",
    "ticket_id": 15,
}


@pytest.fixture(autouse=True)
def clear_processed_events(monkeypatch):
    """Keep each test independent with a fresh event list and token."""
    event_ids.clear()
    monkeypatch.setenv("WEBHOOK_BEARER_TOKEN", TOKEN)


# Accept a valid event when the sender presents the configured token.
def test_receive_event_accepts_authenticated_payload():
    response = client.post(
        "/webhooks/tickets",
        json=PAYLOAD,
        headers={"Authorization": f"Bearer {TOKEN}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "received": True,
        "event_id": "evt_001",
        "ticket_id": 15,
    }


# Reject requests without a valid bearer token.
@pytest.mark.parametrize(
    "authorization",
    [None, "Bearer wrong-token", "Basic test-webhook-token"],
)
def test_receive_event_rejects_invalid_authentication(authorization):
    headers = {}
    if authorization is not None:
        headers["Authorization"] = authorization

    response = client.post("/webhooks/tickets", json=PAYLOAD, headers=headers)

    assert response.status_code == 401


# Return a service error when no webhook token has been configured.
def test_receive_event_rejects_requests_when_authentication_is_unconfigured(
    monkeypatch,
):
    monkeypatch.delenv("WEBHOOK_BEARER_TOKEN")

    response = client.post(
        "/webhooks/tickets",
        json=PAYLOAD,
        headers={"Authorization": f"Bearer {TOKEN}"},
    )

    assert response.status_code == 503


# Reject malformed, incomplete, or unexpected payload data.
@pytest.mark.parametrize(
    "payload",
    [
        {"event_id": "", "event_type": "ticket.created", "ticket_id": 15},
        {"event_id": "evt_001", "event_type": " ", "ticket_id": 15},
        {"event_id": "evt_001", "event_type": "ticket.created", "ticket_id": 0},
        {
            "event_id": "evt_001",
            "event_type": "ticket.created",
            "ticket_id": "15",
        },
        {**PAYLOAD, "unexpected": True},
    ],
)
def test_receive_event_rejects_invalid_payloads(payload):
    response = client.post(
        "/webhooks/tickets",
        json=payload,
        headers={"Authorization": f"Bearer {TOKEN}"},
    )

    assert response.status_code == 422


# Reject a second delivery of an event ID already processed.
def test_receive_event_rejects_duplicate_event():
    headers = {"Authorization": f"Bearer {TOKEN}"}

    first_response = client.post(
        "/webhooks/tickets", json=PAYLOAD, headers=headers
    )
    duplicate_response = client.post(
        "/webhooks/tickets", json=PAYLOAD, headers=headers
    )

    assert first_response.status_code == 200
    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {"detail": "Event already processed."}
