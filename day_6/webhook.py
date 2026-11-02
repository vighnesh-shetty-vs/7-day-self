import os
import secrets
from threading import Lock
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

app = FastAPI()

event_ids = set()
event_ids_lock = Lock()


class TicketEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    event_id: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    event_type: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    ticket_id: int = Field(gt=0)


# Check the token and record each event ID only once.
@app.post("/webhooks/tickets")
def receive_event(
    event: TicketEvent,
    authorization: Annotated[str | None, Header()] = None,
):
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

    with event_ids_lock:
        if event.event_id in event_ids:
            raise HTTPException(status_code=409, detail="Event already processed.")
        event_ids.add(event.event_id)

    return {
        "received": True,
        "event_id": event.event_id,
        "ticket_id": event.ticket_id,
    }
