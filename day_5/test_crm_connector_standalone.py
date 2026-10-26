import unittest
from unittest.mock import MagicMock, patch

import requests


class APIResponseValidationError(ValueError):
    """Raised when the API response is not valid customer data."""


class CRMConnector:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def get_customer(self, customer_id):
        url = f"{self.base_url}/users/{customer_id}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        try:
            customer = response.json()
        except requests.exceptions.JSONDecodeError as error:
            raise APIResponseValidationError(
                "The API response is not valid JSON."
            ) from error

        if not isinstance(customer, dict):
            raise APIResponseValidationError(
                "Expected the API response to be a customer object."
            )

        customer_id_value = customer.get("id")
        if (
            isinstance(customer_id_value, bool)
            or not isinstance(customer_id_value, int)
        ):
            raise APIResponseValidationError(
                "Customer data must contain an integer 'id'."
            )
        if customer_id_value != customer_id:
            raise APIResponseValidationError(
                f"Requested customer ID {customer_id}, but the API returned "
                f"ID {customer_id_value}."
            )

        for field in ("name", "email"):
            value = customer.get(field)
            if not isinstance(value, str) or not value.strip():
                raise APIResponseValidationError(
                    f"Customer data must contain a non-empty string '{field}'."
                )

        return {
            "id": customer_id_value,
            "name": customer["name"],
            "email": customer["email"],
        }


class TestCRMConnector(unittest.TestCase):
    def setUp(self):
        self.connector = CRMConnector("https://crm.example.com/")

    def make_response(self, payload):
        response = MagicMock()
        response.json.return_value = payload
        return response

    @patch("requests.get")
    def test_get_customer_returns_customer_and_uses_timeout(self, get):
        response = self.make_response(
            {"id": 42, "name": "Ada Lovelace", "email": "ada@example.com"}
        )
        get.return_value = response

        customer = self.connector.get_customer(42)

        self.assertEqual(
            customer,
            {"id": 42, "name": "Ada Lovelace", "email": "ada@example.com"},
        )
        get.assert_called_once_with(
            "https://crm.example.com/users/42", timeout=10
        )
        response.raise_for_status.assert_called_once_with()

    @patch("requests.get")
    def test_get_customer_propagates_http_errors(self, get):
        response = self.make_response({})
        error = requests.exceptions.HTTPError("server error")
        response.raise_for_status.side_effect = error
        get.return_value = response

        with self.assertRaises(requests.exceptions.HTTPError) as raised:
            self.connector.get_customer(42)

        self.assertIs(raised.exception, error)
        response.json.assert_not_called()

    @patch("requests.get")
    def test_get_customer_rejects_invalid_json(self, get):
        response = self.make_response({})
        response.json.side_effect = requests.exceptions.JSONDecodeError(
            "invalid", "", 0
        )
        get.return_value = response

        with self.assertRaisesRegex(
            APIResponseValidationError, "not valid JSON"
        ):
            self.connector.get_customer(42)

    @patch("requests.get")
    def test_get_customer_rejects_invalid_customer_data(self, get):
        invalid_payloads = [
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
        ]

        for payload, message in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.make_response(payload)
                get.return_value = response

                with self.assertRaisesRegex(APIResponseValidationError, message):
                    self.connector.get_customer(42)


if __name__ == "__main__":
    unittest.main()
