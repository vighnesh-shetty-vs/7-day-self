import json

import pytest

from day_7.ticket_connector import TicketConnector, TicketSourceError


def test_connector_loads_and_validates_sample_tickets():
    tickets = TicketConnector().get_tickets()

    assert len(tickets) == 5
    assert tickets[0].id == 1001
    assert tickets[0].customer_email == "maya@example.com"


def test_connector_retrieves_ticket_by_id():
    ticket = TicketConnector().get_ticket(1003)

    assert ticket is not None
    assert ticket.subject == "Dashboard keeps loading"
    assert TicketConnector().get_ticket(9999) is None


def test_connector_reports_missing_source_file(tmp_path):
    with pytest.raises(TicketSourceError, match="Could not read ticket source"):
        TicketConnector(tmp_path / "missing.json").get_tickets()


def test_connector_reports_invalid_json(tmp_path):
    source = tmp_path / "tickets.json"
    source.write_text("{", encoding="utf-8")

    with pytest.raises(TicketSourceError, match="not valid JSON"):
        TicketConnector(source).get_tickets()


def test_connector_reports_invalid_utf8(tmp_path):
    source = tmp_path / "tickets.json"
    source.write_bytes(b"\xff")

    with pytest.raises(TicketSourceError, match="not valid UTF-8"):
        TicketConnector(source).get_tickets()


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {
            "id": 1,
            "subject": "",
            "description": "Body",
            "customer_email": "a@b",
            "status": "open",
        },
        {
            "id": 1,
            "subject": "Subject",
            "description": "Body",
            "customer_email": "not-an-email",
            "status": "open",
        },
        {
            "id": 1,
            "subject": "Subject",
            "description": "Body",
            "customer_email": "a@b",
            "status": "unknown",
        },
    ],
)
def test_connector_rejects_malformed_ticket_data(tmp_path, payload):
    source = tmp_path / "tickets.json"
    source.write_text(json.dumps([payload]), encoding="utf-8")

    with pytest.raises(TicketSourceError, match="invalid ticket data"):
        TicketConnector(source).get_tickets()


def test_connector_rejects_non_array_document(tmp_path):
    source = tmp_path / "tickets.json"
    source.write_text(json.dumps({"id": 1}), encoding="utf-8")

    with pytest.raises(TicketSourceError, match="JSON array"):
        TicketConnector(source).get_tickets()
