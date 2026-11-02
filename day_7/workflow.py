"""Deterministic ticket classification used by the support workflow."""

from typing import Literal

TicketCategory = Literal["billing", "technical", "account-related"]

BILLING_KEYWORDS = (
    "bill",
    "billing",
    "charge",
    "charged",
    "credit",
    "invoice",
    "payment",
    "price",
    "refund",
    "subscription",
)
ACCOUNT_KEYWORDS = (
    "account",
    "email",
    "login",
    "password",
    "profile",
    "sign in",
    "username",
)


def classify_ticket(subject: str, description: str) -> TicketCategory:
    """Classify a ticket by keywords; unmatched tickets default to technical."""
    text = f"{subject} {description}".casefold()
    if any(keyword in text for keyword in BILLING_KEYWORDS):
        return "billing"
    if any(keyword in text for keyword in ACCOUNT_KEYWORDS):
        return "account-related"
    return "technical"
