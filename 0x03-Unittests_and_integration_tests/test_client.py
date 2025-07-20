#!/usr/bin/env python3
"""
Unit and integration tests for the client module, specifically
the GithubOrgClient class.
"""

import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
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
    @patch('client.get_json')
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

        client = GithubOrgClient(org_name)
        result = client.org()

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

            client = GithubOrgClient("test_org")
            result = client._public_repos_url  # Access the property

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
        # Payload that mock_get_json will return when called
        # This structure must match what GithubOrgClient.public_repos expects
        test_payload = [
            {"name": "alx-backend", "license": {"key": "mit"}},
            {"name": "alx-frontend", "license": {"key": "apache-2.0"}},
            {"name": "alx-devops"},  # Repo with no license
        ]
        mock_get_json.return_value = test_payload

        # Mock the _public_repos_url property using patch as a context manager
        # PropertyMock is essential for mocking properties
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_public_repos_url:
            # Set the return value for the mocked property. Max 79 chars.
            mock_public_repos_url.return_value = \
                "https://api.github.com/orgs/some_org/repos"

            # Create an instance of GithubOrgClient
            # The 'org' argument here is just a placeholder, as the actual API
            # call for the organization's data is bypassed by the
            # _public_repos_url mock.
            test_client = GithubOrgClient("holberton")

            # Call the method under test
            repos = test_client.public_repos()

            # Assertions
            # The expected list of repos (only names) based on our test_payload
            expected_repos_names = ["alx-backend", "alx-frontend", "alx-devops"]
            self.assertEqual(repos, expected_repos_names)

            # Verify that the mocked _public_repos_url property was accessed
            # exactly once
            mock_public_repos_url.assert_called_once()

            # Verify that the mocked get_json method was called exactly once
            # with the URL returned by the _public_repos_url mock
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


@parameterized_class(FIXTURES)  # Use the correctly imported FIXTURES
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient.public_repos.
    Mocks external HTTP requests using requests.get.
    """
    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up class-level mocks for requests.get.
        This will intercept all calls to requests.get made by utils.get_json.
        """
        # Create mock response objects for the two expected calls
        # to requests.get:
        # 1. For the organization payload (from client.org)
        mock_org_response = Mock()
        mock_org_response.json.return_value = cls.org_payload
        mock_org_response.raise_for_status.return_value = None

        # 2. For the repositories payload (from client.public_repos)
        mock_repos_response = Mock()
        mock_repos_response.json.return_value = cls.repos_payload
        mock_repos_response.raise_for_status.return_value = None

        # Start patching 'requests.get'.
        # The 'side_effect' list provides responses sequentially.
        cls.get_patcher = patch(
            'requests.get',
            side_effect=[mock_org_response, mock_repos_response]
        )
        cls.mock_get = cls.get_patcher.start()

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
        client = GithubOrgClient("google")
        # Ensure public_repos is called as a method
        actual_repos = client.public_repos()

        self.assertEqual(self.mock_get.call_count, 2)

        # Check call arguments for each call to requests.get
        expected_org_url = "https://api.github.com/orgs/google"
        # Access positional arguments using .args[0]
        self.assertEqual(self.mock_get.call_args_list[0].args[0],
                         expected_org_url) # E501 line too long

        # The repos_url comes from the org_payload, which is a class attribute
        expected_repos_url = self.org_payload["repos_url"]
        self.assertEqual(self.mock_get.call_args_list[1].args[0],
                         expected_repos_url) # E501 line too long

        # The public_repos method should return only the names.
        self.assertEqual(actual_repos, self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """
        Tests the public_repos method with a license filter.
        """
        client = GithubOrgClient("google")
        # Ensure public_repos is called as a method
        actual_repos = client.public_repos("apache-2.0")

        # The public_repos method with a license filter should return names.
        self.assertEqual(actual_repos, self.apache2_repos)
        self.assertEqual(self.mock_get.call_count, 2)  # Should still be 2 calls

        # Verify call arguments
        expected_org_url = "https://api.github.com/orgs/google"
        self.assertEqual(self.mock_get.call_args_list[0].args[0],
                         expected_org_url) # E501 line too long

        expected_repos_url = self.org_payload["repos_url"]
        self.assertEqual(self.mock_get.call_args_list[1].args[0],
                         expected_repos_url) # E501 line too long