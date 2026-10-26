from unittest.mock import MagicMock

import pytest
import requests

from day_4.crm_connector import APIResponseValidationError, CRMConnector


def _mock_response(payload):
    response = MagicMock()
    response.json.return_value = payload
    return response


def test_get_customer_requests_and_returns_customer(monkeypatch):
    response = _mock_response(
        {"id": 42, "name": "Ada Lovelace", "email": "ada@example.com"}
    )
    get = MagicMock(return_value=response)
    monkeypatch.setattr("day_4.crm_connector.requests.get", get)
    connector = CRMConnector("https://crm.example.com/now")

    customer = connector.get_customer(42)

    assert customer == {
        "id": 42,
        "name": "Ada Lovelace",
        "email": "ada@example.com",
    }
    get.assert_called_once_with(
        "https://crm.example.com/now/users/42", timeout=10
    )
    response.raise_for_status.assert_called_once_with()


def test_get_customer_propagates_http_errors(monkeypatch):
    response = _mock_response({})
    error = requests.exceptions.HTTPError("server error")
    response.raise_for_status.side_effect = error
    monkeypatch.setattr(
        "day_4.crm_connector.requests.get", MagicMock(return_value=response)
    )
    connector = CRMConnector("https://crm.example.com")

    with pytest.raises(requests.exceptions.HTTPError) as raised:
        connector.get_customer(42)

    assert raised.value is error
    response.json.assert_not_called()


def test_get_customer_rejects_invalid_json(monkeypatch):
    response = _mock_response({})
    response.json.side_effect = requests.exceptions.JSONDecodeError("invalid", "", 0)
    monkeypatch.setattr(
        "day_4.crm_connector.requests.get", MagicMock(return_value=response)
    )
    connector = CRMConnector("https://crm.example.com")

    with pytest.raises(APIResponseValidationError, match="not valid JSON"):
        connector.get_customer(42)


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ([], "Expected the API response to be a customer object"),
        ({"name": "Ada", "email": "ada@example.com"}, "integer 'id'"),
        (
            {"id": True, "name": "Ada", "email": "ada@example.com"},
            "integer 'id'",
        ),
        (
            {"id": 7, "name": "Ada", "email": "ada@example.com"},
            "Requested customer ID 42",
        ),
        (
            {"id": 42, "email": "ada@example.com"},
            "non-empty string 'name'",
        ),
        (
            {"id": 42, "name": "Ada", "email": " "},
            "non-empty string 'email'",
        ),
    ],
)
def test_get_customer_rejects_invalid_customer_data(monkeypatch, payload, message):
    response = _mock_response(payload)
    monkeypatch.setattr(
        "day_4.crm_connector.requests.get", MagicMock(return_value=response)
    )
    connector = CRMConnector("https://crm.example.com")

    with pytest.raises(APIResponseValidationError, match=message):
        connector.get_customer(42)
