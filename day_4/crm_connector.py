from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import time

import requests


class APIResponseValidationError(ValueError):
    """Raised when the API response is not valid customer data."""


class CRMConnector:
    # Store the API address and retry settings.
    def __init__(self, base_url, rate_limit_retries=3, backoff_factor=1):
        if rate_limit_retries < 0:
            raise ValueError("rate_limit_retries cannot be negative.")
        if backoff_factor < 0:
            raise ValueError("backoff_factor cannot be negative.")

        self.base_url = base_url.rstrip("/")
        self.rate_limit_retries = rate_limit_retries
        self.backoff_factor = backoff_factor

    # Send a request and retry when the API rate limit is reached.
    def _get(self, url, params=None):
        for attempt in range(self.rate_limit_retries + 1):
            if params is None:
                response = requests.get(url, timeout=10)
            else:
                response = requests.get(url, params=params, timeout=10)
            if response.status_code != 429:
                response.raise_for_status()
                return response

            if attempt == self.rate_limit_retries:
                response.raise_for_status()

            retry_after = response.headers.get("Retry-After")
            try:
                delay = float(retry_after)
            except (TypeError, ValueError):
                try:
                    retry_at = parsedate_to_datetime(retry_after)
                    if retry_at.tzinfo is None:
                        retry_at = retry_at.replace(tzinfo=timezone.utc)
                    delay = max(
                        0,
                        (retry_at - datetime.now(timezone.utc)).total_seconds(),
                    )
                except (TypeError, ValueError, OverflowError):
                    delay = self.backoff_factor * (2**attempt)

            time.sleep(delay)

    # Retrieve and validate one customer by ID.
    def get_customer(self, customer_id):
        url = f"{self.base_url}/users/{customer_id}"

        response = self._get(url)

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

        return self._validate_customer(customer, customer_id)

    def get_customers(self, page_size=10):
        """Fetch all customers using JSONPlaceholder's _page/_limit pagination."""
        if page_size <= 0:
            raise ValueError("page_size must be greater than zero.")

        customers = []
        page = 1
        while True:
            response = self._get(
                f"{self.base_url}/users",
                params={"_page": page, "_limit": page_size},
            )
            try:
                page_customers = response.json()
            except requests.exceptions.JSONDecodeError as error:
                raise APIResponseValidationError(
                    "The API response is not valid JSON."
                ) from error

            if not isinstance(page_customers, list):
                raise APIResponseValidationError(
                    "Expected the API response to be a list of customers."
                )

            customers.extend(
                self._validate_customer(customer) for customer in page_customers
            )
            if len(page_customers) < page_size:
                return customers
            page += 1

    # Check that customer data has the expected fields and values.
    @staticmethod
    def _validate_customer(customer, expected_id=None):
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
        if expected_id is not None and customer_id_value != expected_id:
            raise APIResponseValidationError(
                f"Requested customer ID {expected_id}, but the API returned "
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


# Fetch every customer and print the results or report a request error.
def main():
    crm = CRMConnector("https://jsonplaceholder.typicode.com")

    try:
        customers = crm.get_customers(page_size=3)
    except requests.exceptions.Timeout as error:
        print(f"Network timeout while retrieving customers: {error}")
        raise SystemExit(1) from error
    except requests.exceptions.ConnectionError as error:
        print(f"Network connection failed while retrieving customers: {error}")
        raise SystemExit(1) from error
    except requests.exceptions.HTTPError as error:
        status_code = error.response.status_code if error.response is not None else "unknown"
        print(f"HTTP error {status_code} while retrieving customers: {error}")
        raise SystemExit(1) from error
    except requests.exceptions.RequestException as error:
        print(f"Request failed while retrieving customers: {error}")
        raise SystemExit(1) from error
    except APIResponseValidationError as error:
        print(f"Invalid customer data received from the API: {error}")
        raise SystemExit(1) from error

    print(customers)


if __name__ == "__main__":
    main()