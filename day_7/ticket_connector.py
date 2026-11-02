"""Validated local JSON connector for support tickets."""

import json
from pathlib import Path
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    ValidationError,
)

class TicketSourceError(RuntimeError):
    """Raised when the ticket source cannot be read or validated."""


class Ticket(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int = Field(gt=0)
    subject: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    description: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1)
    ]
    customer_email: EmailStr
    status: Literal["open", "pending", "closed"]


class TicketConnector:
    """Read tickets from a local JSON file and validate their shape."""

    def __init__(self, source_path: str | Path | None = None):
        self.source_path = (
            Path(source_path) if source_path is not None
            else Path(__file__).with_name("tickets.json")
        )

    def get_tickets(self) -> list[Ticket]:
        try:
            with self.source_path.open(encoding="utf-8") as source:
                payload = json.load(source)
        except OSError as error:
            raise TicketSourceError(
                f"Could not read ticket source '{self.source_path}'."
            ) from error
        except UnicodeDecodeError as error:
            raise TicketSourceError(
                f"Ticket source '{self.source_path}' is not valid UTF-8."
            ) from error
        except json.JSONDecodeError as error:
            raise TicketSourceError(
                f"Ticket source '{self.source_path}' is not valid JSON."
            ) from error

        if not isinstance(payload, list):
            raise TicketSourceError("Ticket source must contain a JSON array.")

        try:
            return [Ticket.model_validate(item) for item in payload]
        except ValidationError as error:
            raise TicketSourceError(
                f"Ticket source contains invalid ticket data: {error}"
            ) from error

    def get_ticket(self, ticket_id: int) -> Ticket | None:
        return next(
            (ticket for ticket in self.get_tickets() if ticket.id == ticket_id),
            None,
        )
