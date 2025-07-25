#!/usr/bin/env python3
"""
Unit and integration tests for the client module, specifically
the GithubOrgClient class.
"""

import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient, get_json # Ensure get_json is imported from client
from typing import (
    Dict,
    Any,
    List
)
# Correctly import FIXTURES as a list of tuples from fixtures.py
from fixtures import FIXTURES


class TestGithubOrgClient(unittest.TestCase):
    """
    Unit tests for the GithubOrgClient class.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json') # This remains correct for unit tests of test_org
    def test_org(self, org_name: str, mock_get_json: Mock) -> None:
        """
        Test that GithubOrgClient.org returns the correct value.
        """
        expected_payload = {
            "login": org_name,
            "id": 123,
            "repos_url": f"https://api.github.com/orgs/{org_name}/repos"
        }
        mock_get_json.return_value = expected_payload

        client_instance = GithubOrgClient(org_name)
        result = client_instance.org()

        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, expected_payload)

    def test_public_repos_url(self) -> None:
        """
        Tests that _public_repos_url returns the expected URL
        based on a mocked GithubOrgClient.org property using
        patch as a context manager.
        """
        expected_repos_url = "https://api.github.com/users/octocat/repos"
        test_org_payload = {"repos_url": expected_repos_url}

        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            mock_org.return_value = test_org_payload

            client_instance = GithubOrgClient("test_org")
            result = client_instance._public_repos_url  # Access the property

            # Assertions
            mock_org.assert_called_once()
            self.assertEqual(result, expected_repos_url)

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """
        Tests the GithubOrgClient.public_repos method.

        Mocks `get_json` to return a specific payload and
        mocks `_public_repos_url` as a property.
        Verifies that the correct list of repos is returned and
        that the mocks were called as expected.
        """
        test_payload = [
            {"name": "alx-backend", "license": {"key": "mit"}},
            {"name": "alx-frontend", "license": {"key": "apache-2.0"}},
            {"name": "alx-devops"},
        ]
        mock_get_json.return_value = test_payload

        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = \
                "https://api.github.com/orgs/some_org/repos"

            test_client_instance = GithubOrgClient("holberton")
            repos = test_client_instance.public_repos()

            expected_repos_names = ["alx-backend", "alx-frontend",
                                    "alx-devops"]
            self.assertEqual(repos, expected_repos_names)

            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(
                "https://api.github.com/orgs/some_org/repos"
            )

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": {"key": "my_license"}}, "other_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
        ({"name": "test-repo",
          "license": {"key": "my_license", "name": "MIT"}},
         "my_license", True),
        ({"license": {}}, "my_license", False),
    ])
    def test_has_license(self, repo: Dict[str, Any],
                         license_key: str, expected_result: bool) -> None:
        """
        Tests that GithubOrgClient.has_license returns the
        expected boolean value.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected_result)


@parameterized_class(FIXTURES)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient.public_repos.
    Mocks external HTTP requests using requests.get (via get_json).
    """
    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up class-level mocks for the `get_json` function.
        This will intercept all calls to `get_json` made by `GithubOrgClient`.
        """
        # Create mock response objects for the two expected calls
        # to get_json:
        # 1. For the organization payload (from client.org)
        # 2. For the repositories payload (from client.public_repos)
        # Note: get_json returns the .json() value directly, not a Response object
        side_effects_list = [
            cls.org_payload,    # First call to get_json (for org)
            cls.repos_payload   # Second call to get_json (for repos)
        ]

        # Patch `get_json` directly in the `client` module where it's used.
        # This is generally more robust for integration tests when
        # get_json is the actual network fetching function.
        cls.get_patcher = patch(
            'client.get_json',  # Patching the get_json function itself
            side_effect=side_effects_list
        )
        cls.mock_get_json = cls.get_patcher.start() # Rename mock to be explicit

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Stop the patcher after all tests in this class have run.
        """
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """
        Tests GithubOrgClient.public_repos in an integration context.
        """
        client_instance = GithubOrgClient("google")
        actual_repos = client_instance.public_repos()

        # Check that get_json was called twice
        self.assertEqual(self.mock_get_json.call_count, 2)

        # Check call arguments for each call to get_json
        expected_org_url = "https://api.github.com/orgs/google"
        self.assertEqual(self.mock_get_json.call_args_list[0].args[0],
                         expected_org_url)

        expected_repos_url = self.org_payload["repos_url"]
        self.assertEqual(self.mock_get_json.call_args_list[1].args[0],
                         expected_repos_url)

        self.assertEqual(actual_repos, self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """
        Tests the public_repos method with a license filter.
        """
        client_instance = GithubOrgClient("google")
        actual_repos = client_instance.public_repos("apache-2.0")

        self.assertEqual(actual_repos, self.apache2_repos)
        self.assertEqual(self.mock_get_json.call_count, 2) # Still 2 calls to get_json

        expected_org_url = "https://api.github.com/orgs/google"
        self.assertEqual(self.mock_get_json.call_args_list[0].args[0],
                         expected_org_url)

        expected_repos_url = self.org_payload["repos_url"]
        self.assertEqual(self.mock_get_json.call_args_list[1].args[0],
                         expected_repos_url)