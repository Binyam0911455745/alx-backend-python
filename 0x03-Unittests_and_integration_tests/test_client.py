#!/usr/bin/env python3
"""
Unit tests for the client.GithubOrgClient class.
"""

import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient  # Assuming client.py is in the project root
# Corrected E261 and E501: at least two spaces before comments and line length
from typing import (
    Dict,
    Any,
    List
)


class TestGithubOrgClient(unittest.TestCase):
    """
    Tests for the GithubOrgClient class.
    """

    @parameterized.expand([
        ("google", {"login": "google", "id": 123}),
        ("abc", {"login": "abc", "id": 456}),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, test_payload: Dict, mock_get_json: Mock):
        """
        Tests that GithubOrgClient.org returns the correct value.
        Mocks get_json to prevent external HTTP calls.
        """
        mock_get_json.return_value = test_payload

        client = GithubOrgClient(org_name)
        result = client.org()

        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, test_payload)

    @patch('client.GithubOrgClient.org', new_callable=PropertyMock)
    def test_public_repos_url(self, mock_org: PropertyMock):
        """
        Tests that _public_repos_url returns the expected URL
        based on a mocked GithubOrgClient.org property.
        """
        expected_repos_url = "https://api.github.com/users/octocat/repos"
        test_org_payload = {"repos_url": expected_repos_url}
        mock_org.return_value = test_org_payload

        client = GithubOrgClient("test_org")
        result = client._public_repos_url

        mock_org.assert_called_once()
        self.assertEqual(result, expected_repos_url)

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: Mock):  # Corrected E261
        """
        Tests GithubOrgClient.public_repos by mocking get_json and
        _public_repos_url. Verifies correct calls and returned data.
        """
        # 1. Define the payload that mock_get_json will return
        #    This simulates the response from the GitHub API for repos
        test_repos_payload: List[Dict[str, Any]] = [
            {"name": "alx-backend", "license": {"key": "mit"}},
            {"name": "alx-frontend", "license": {"key": "apache-2.0"}},
            {"name": "alx-fullstack", "license": {"key": "gpl-3.0"}}
        ]
        mock_get_json.return_value = test_repos_payload

        # 2. Define the URL that the mocked _public_repos_url property will return
        #    This is the URL that public_repos will pass to get_json
        # Corrected E501: line too long
        expected_repos_api_url = "https://api.github.com/orgs/mock_org/repos"

        # 3. Patch _public_repos_url as a context manager (it's a property)
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = expected_repos_api_url

            # Instantiate GithubOrgClient. The org_name passed to __init__
            # doesn't directly affect this test since .org and
            # _public_repos_url are being mocked.
            client = GithubOrgClient("mock_org")

            # Call public_repos. Assuming it's a property or memoized property
            # that internally calls _public_repos_url and then get_json.
            result = client.public_repos

            # Assertions:
            # 1. Test that the list of repos returned is what we expect
            self.assertEqual(result, test_repos_payload)

            # 2. Test that _public_repos_url property was accessed once
            mock_public_repos_url.assert_called_once()

            # 3. Test that get_json was called once with the expected API URL
            mock_get_json.assert_called_once_with(expected_repos_api_url)
