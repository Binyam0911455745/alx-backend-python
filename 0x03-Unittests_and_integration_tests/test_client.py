#!/usr/bin/env python3
"""
Unit tests and integration tests for client.py.
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
# Import fixtures from accounts.fixtures
from fixtures import ORG_PAYLOAD, REPOS_PAYLOAD, EXPECTED_REPOS, APACHE2_REPOS


class TestGithubOrgClient(unittest.TestCase):
    """
    Unit tests for the GithubOrgClient class.
    """

    @parameterized.expand([
        ("google",),  # Parametrized test case for 'google' org
        ("abc",),     # Parametrized test case for 'abc' org
    ])
    @patch(
        'client.get_json'
    )  # Patch 'get_json' where it's imported in client.py
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


    def test_public_repos_url(self):
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


    @patch('client.get_json')  # Mock get_json as a decorator
    def test_public_repos(self, mock_get_json: Mock):
        """
        Tests GithubOrgClient.public_repos by mocking get_json
        and _public_repos_url.
        Verifies correct calls and returned data for Task 6.
        """
        test_repos_payload: List[Dict[str, Any]] = [
            {"name": "alx-backend", "license": {"key": "mit"}},
            {"name": "alx-frontend", "license": {"key": "apache-2.0"}},
            {"name": "alx-fullstack", "license": {"key": "gpl-3.0"}}
        ]
        mock_get_json.return_value = test_repos_payload

        # This is the URL that _public_repos_url would return
        expected_repos_api_url = \
            "https://api.github.com/orgs/mock_org/repos"

        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = expected_repos_api_url

            client = GithubOrgClient("mock_org")
            result = client.public_repos

            self.assertEqual(result, test_repos_payload)
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(expected_repos_api_url)


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
                         license_key: str, expected_result: bool):
        """
        Tests that GithubOrgClient.has_license returns the
        expected boolean value.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected_result)


@parameterized_class([
    {
        "org_payload": ORG_PAYLOAD,
        "repos_payload": REPOS_PAYLOAD,
        "expected_repos": EXPECTED_REPOS,
        "apache2_repos": APACHE2_REPOS,
    },
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient.public_repos.
    Mocks external HTTP requests using requests.get.
    """
    @classmethod
    def setUpClass(cls):
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
        cls.get_patcher = patch('requests.get',
                                 side_effect=[mock_org_response,
                                              mock_repos_response])
        cls.mock_get = cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """
        Stop the patcher after all tests in this class have run.
        """
        cls.get_patcher.stop()

    def test_public_repos(self):
        """
        Tests GithubOrgClient.public_repos in an integration context.
        """
        client = GithubOrgClient("google")
        actual_repos = client.public_repos() # public_repos is a method now

        self.assertEqual(self.mock_get.call_count, 2)

        expected_org_url = "https://api.github.com/orgs/google"
        self.mock_get.call_args_list[0].assert_called_with(expected_org_url)

        expected_repos_url = self.org_payload["repos_url"]
        self.mock_get.call_args_list[1].assert_called_with(expected_repos_url)

        # Extract names from actual_repos based on the fixture structure
        extracted_names = [repo["name"] for repo in actual_repos]
        self.assertEqual(extracted_names, self.expected_repos)

    def test_public_repos_with_license(self):
        """
        Tests the public_repos method with a license filter.
        """
        client = GithubOrgClient("google")
        actual_repos = client.public_repos("apache-2.0")

        # Extract names from actual_repos based on the fixture structure
        extracted_names = [repo["name"] for repo in actual_repos]
        self.assertEqual(extracted_names, self.apache2_repos)
        self.assertEqual(self.mock_get.call_count, 2) # Should still be 2 calls

        expected_org_url = "https://api.github.com/orgs/google"
        self.mock_get.call_args_list[0].assert_called_with(expected_org_url)

        expected_repos_url = self.org_payload["repos_url"]
        self.mock_get.call_args_list[1].assert_called_with(expected_repos_url)