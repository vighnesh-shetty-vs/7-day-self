from unittest.mock import MagicMock, call

import pytest
import requests

from day_4.crm_connector import APIResponseValidationError, CRMConnector, main


# Build a fake API response for tests.
def _mock_response(payload):
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = payload
    return response


# Check that a customer is requested and returned correctly.
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


# Check that API errors are passed back to the caller.
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


# Check that unreadable JSON is reported as invalid customer data.
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
# Check that incomplete or mismatched customer data is rejected.
def test_get_customer_rejects_invalid_customer_data(monkeypatch, payload, message):
    response = _mock_response(payload)
    monkeypatch.setattr(
        "day_4.crm_connector.requests.get", MagicMock(return_value=response)
    )
    connector = CRMConnector("https://crm.example.com")

    with pytest.raises(APIResponseValidationError, match=message):
        connector.get_customer(42)


# Check that a rate-limited request waits and then retries.
def test_get_customer_retries_rate_limit_using_retry_after(monkeypatch):
    limited_response = MagicMock(status_code=429)
    limited_response.headers = {"Retry-After": "2"}
    customer_response = _mock_response(
        {"id": 42, "name": "Ada Lovelace", "email": "ada@example.com"}
    )
    get = MagicMock(side_effect=[limited_response, customer_response])
    sleep = MagicMock()
    monkeypatch.setattr("day_4.crm_connector.requests.get", get)
    monkeypatch.setattr("day_4.crm_connector.time.sleep", sleep)
    connector = CRMConnector("https://crm.example.com")

    customer = connector.get_customer(42)

    assert customer["id"] == 42
    assert get.call_count == 2
    sleep.assert_called_once_with(2)


# Check that every customer page is requested and combined.
def test_get_customers_fetches_pages_until_the_last_page(monkeypatch):
    first_page = _mock_response(
        [
            {"id": 1, "name": "Ada", "email": "ada@example.com"},
            {"id": 2, "name": "Grace", "email": "grace@example.com"},
        ]
    )
    last_page = _mock_response(
        [{"id": 3, "name": "Katherine", "email": "katherine@example.com"}]
    )
    get = MagicMock(side_effect=[first_page, last_page])
    monkeypatch.setattr("day_4.crm_connector.requests.get", get)
    connector = CRMConnector("https://crm.example.com")

    customers = connector.get_customers(page_size=2)

    assert [customer["id"] for customer in customers] == [1, 2, 3]
    assert get.call_args_list == [
        call(
            "https://crm.example.com/users",
            params={"_page": 1, "_limit": 2},
            timeout=10,
        ),
        call(
            "https://crm.example.com/users",
            params={"_page": 2, "_limit": 2},
            timeout=10,
        ),
    ]


# Check that the script fetches and displays the full customer list.
def test_main_fetches_and_prints_all_customers(monkeypatch, capsys):
    customers = [
        {"id": 1, "name": "Ada", "email": "ada@example.com"},
        {"id": 2, "name": "Grace", "email": "grace@example.com"},
    ]
    connector = MagicMock()
    connector.get_customers.return_value = customers
    crm_connector = MagicMock(return_value=connector)
    monkeypatch.setattr("day_4.crm_connector.CRMConnector", crm_connector)

    main()

    connector.get_customers.assert_called_once_with(page_size=3)
    assert capsys.readouterr().out == f"{customers}\n"
