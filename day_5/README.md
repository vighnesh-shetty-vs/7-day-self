# Day 5 — Testing, debugging and production reliability

## Objective

Learn to prove that the CRM connector works, including when the external
system fails. StackMint explicitly expects thorough integration testing,
including authentication flows, pagination, API schemas, and rate limits.

## Activities

1. Test the Day 4 `CRMConnector` with mocked HTTP responses so the unit tests
   are repeatable and do not depend on network access.
2. Verify that customer data is normalized correctly and that requests use the
   expected URL and timeout.
3. Exercise failure cases: HTTP errors, invalid JSON, and missing, malformed,
   or mismatched customer fields.
4. Run the same core checks from a self-contained file using Python's built-in
   `unittest` framework.
5. Compare this unit-test coverage with the integration testing needed for a
   production connector.

## Files

- [`test_crm_connector.py`](./test_crm_connector.py) — pytest tests for the
  implementation in [`day_4/crm_connector.py`](../day_4/crm_connector.py).
- [`test_crm_connector_standalone.py`](./test_crm_connector_standalone.py) —
  a standalone copy of the connector and its `unittest` tests; it does not
  import the Day 4 module.
- [`test_sample.py`](./test_sample.py) — a basic pytest example unrelated to
  CRM behavior. Its second assertion currently fails because a string does
  not have a `check` attribute.

The current tests use mocks. They do **not** yet exercise a live integration,
authentication or OAuth flows, pagination, schema compatibility/versioning,
or rate-limit handling. These should be added for thorough production-level
integration coverage.

## Run

From the repository root, run the CRM connector tests with pytest:

```bash
python -m pytest day_5/test_crm_connector.py day_5/test_crm_connector_standalone.py -q
```

Run the standalone `unittest` program directly:

```bash
python day_5/test_crm_connector_standalone.py
```

To run every test in the folder, including the introductory sample:

```bash
python -m pytest day_5 -q
```

## Results

The two CRM test files pass: **13 tests passed**, with **6 validation
subtests passed**. The standalone file also passes when run directly: **4
tests passed**.

The full Day 5 folder run has **14 passing tests and one failing test**, plus
**6 validation subtests passed**. The failure is
`test_sample.py::TestClass::test_two`, which is the unrelated sample
assertion described above.

## Success criteria

- Confirm successful customer retrieval and expected request configuration.
- Verify that HTTP and malformed-response failures surface as errors instead
  of being treated as successful customer data.
- Recognize the difference between mocked unit tests and integration tests.
- Identify authentication, pagination, API schemas, and rate limits as
  integration scenarios still needing coverage.
