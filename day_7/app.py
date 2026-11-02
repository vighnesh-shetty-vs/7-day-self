"""FastAPI service for searching and retrieving support tickets."""

import os
import secrets
from threading import Lock
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Path as PathParameter, Query
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from day_7.ticket_connector import Ticket, TicketConnector, TicketSourceError
from day_7.workflow import TicketCategory, classify_ticket

app = FastAPI(title="AI Support Ticket Integration", version="1.0.0")
connector = TicketConnector()
processed_event_ids: set[str] = set()
processed_event_ids_lock = Lock()


class TicketResponse(BaseModel):
    id: int
    subject: str
    description: str
    customer_email: str
    status: str
    category: TicketCategory


class TicketSearchResponse(BaseModel):
    count: int
    tickets: list[TicketResponse]


class TicketEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    event_id: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    event_type: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    ticket_id: int = Field(gt=0)


def _to_response(ticket: Ticket) -> TicketResponse:
    return TicketResponse(
        **ticket.model_dump(),
        category=classify_ticket(ticket.subject, ticket.description),
    )


def _load_tickets() -> list[Ticket]:
    try:
        return connector.get_tickets()
    except TicketSourceError as error:
        raise HTTPException(
            status_code=500, detail="Ticket source is unavailable or invalid."
        ) from error


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tickets", response_model=TicketSearchResponse)
def search_tickets(
    q: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    category: TicketCategory | None = None,
) -> TicketSearchResponse:
    tickets = _load_tickets()
    if q is not None:
        search_text = q.casefold()
        tickets = [
            ticket
            for ticket in tickets
            if search_text in ticket.subject.casefold()
            or search_text in ticket.description.casefold()
            or search_text in ticket.customer_email.casefold()
        ]

    results = [
        _to_response(ticket)
        for ticket in tickets
        if category is None
        or classify_ticket(ticket.subject, ticket.description) == category
    ]
    return TicketSearchResponse(count=len(results), tickets=results)


@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: Annotated[int, PathParameter(gt=0)],
) -> TicketResponse:
    ticket = next(
        (ticket for ticket in _load_tickets() if ticket.id == ticket_id),
        None,
    )
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    return _to_response(ticket)


@app.post("/webhooks/tickets", status_code=202)
def receive_ticket_event(
    event: TicketEvent,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, int | str | bool]:
    expected_token = os.environ.get("WEBHOOK_BEARER_TOKEN")
    if not expected_token:
        raise HTTPException(
            status_code=503,
            detail="Webhook authentication is not configured.",
        )

    scheme, separator, supplied_token = (authorization or "").partition(" ")
    if (
        not separator
        or scheme.lower() != "bearer"
        or not secrets.compare_digest(
            supplied_token.encode("utf-8"),
            expected_token.encode("utf-8"),
        )
    ):
        raise HTTPException(status_code=401, detail="Invalid webhook token.")

    with processed_event_ids_lock:
        if event.event_id in processed_event_ids:
            raise HTTPException(status_code=409, detail="Event already processed.")
        processed_event_ids.add(event.event_id)

    return {
        "received": True,
        "event_id": event.event_id,
        "ticket_id": event.ticket_id,
    }
