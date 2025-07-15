#!/usr/bin/env python3
"""
Unit tests for the client.GithubOrgClient class.
"""

import unittest
from unittest.mock import patch, Mock, PropertyMock # Import PropertyMock
from parameterized import parameterized
from client import GithubOrgClient
from typing import Dict, Any


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

    # New test method for Task 5
    @patch('client.GithubOrgClient.org', new_callable=PropertyMock)
    def test_public_repos_url(self, mock_org: PropertyMock):
        """
        Tests that _public_repos_url returns the expected URL
        based on a mocked GithubOrgClient.org property.
        """
        # Define the payload that the mocked .org property will return.
        # It MUST contain the 'repos_url' key that _public_repos_url expects.
        expected_repos_url = "https://api.github.com/users/octocat/repos"
        test_org_payload = {"repos_url": expected_repos_url}
        mock_org.return_value = test_org_payload

        # Instantiate GithubOrgClient. The org_name passed to __init__
        # doesn't directly matter here because GithubOrgClient.org is mocked.
        client = GithubOrgClient("test_org")

        # Access the _public_repos_url property.
        # This will internally access the mocked self.org.
        result = client._public_repos_url

        # Assertions:
        # 1. Verify that the .org property was accessed exactly once.
        mock_org.assert_called_once()

        # 2. Verify that the result from _public_repos_url matches
        #    the expected URL from our mocked payload.
        self.assertEqual(result, expected_repos_url)
