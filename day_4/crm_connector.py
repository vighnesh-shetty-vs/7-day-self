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
            "email": customer["email"]
        }


crm = CRMConnector(
    "https://jsonplaceholder.typicode.com"
)

try:
    customer = crm.get_customer(1)
except requests.exceptions.Timeout as error:
    print(f"Network timeout while retrieving customer: {error}")
    raise SystemExit(1) from error
except requests.exceptions.ConnectionError as error:
    print(f"Network connection failed while retrieving customer: {error}")
    raise SystemExit(1) from error
except requests.exceptions.HTTPError as error:
    status_code = error.response.status_code if error.response is not None else "unknown"
    print(f"HTTP error {status_code} while retrieving customer: {error}")
    raise SystemExit(1) from error
except requests.exceptions.RequestException as error:
    print(f"Request failed while retrieving customer: {error}")
    raise SystemExit(1) from error
except APIResponseValidationError as error:
    print(f"Invalid customer data received from the API: {error}")
    raise SystemExit(1) from error

print(customer)