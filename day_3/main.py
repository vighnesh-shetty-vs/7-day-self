from fastapi import FastAPI, HTTPException

app = FastAPI()

tickets = [
    {"id": 1, "subject": "Payment failed", "status": "open"},
    {"id": 2, "subject": "Login issue", "status": "closed"},
]


# Report whether the ticket service is running.
@app.get("/health")
def get_health():
    return {"status": "ok"}


# Return all tickets, or only those matching a requested status.
@app.get("/tickets")
def get_tickets(status: str | None = None):
    if status is not None:
        return [ticket for ticket in tickets if ticket["status"] == status]
    return tickets


# Find one ticket by ID or return a not-found response.
@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    raise HTTPException(
        status_code=404,
        detail="Ticket not found"
    )