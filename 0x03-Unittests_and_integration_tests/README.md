# 0x03-Unittests_and_integration_tests

This project focuses on understanding and implementing unit tests and integration tests in Python. It involves using the `unittest` framework, mocking external dependencies, and parametrizing tests.

## Files:
- `utils.py`: Contains utility functions like `access_nested_map`, `get_json`, and `memoize`.
- `client.py`: Implements a GitHub organization client that uses the utility functions.
- `fixtures.py`: Provides test data for the client and utility tests.
- `test_utils.py`: Contains unit tests for the `utils` module.
- `test_client.py`: (Will contain) Unit and integration tests for the `GithubOrgClient`.

## How to Run Tests:
1.  Navigate to the project root directory.
2.  Activate the Python virtual environment: `.\.env\Scripts\activate` (Windows) or `source ./.env/bin/activate` (Linux/macOS).
3.  Install necessary packages: `pip install parameterized`
4.  Run tests using: `python -m unittest accounts.test_utils` (adjust path as needed for other test files).
