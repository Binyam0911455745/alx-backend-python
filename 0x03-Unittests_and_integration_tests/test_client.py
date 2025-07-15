#!/usr/bin/env python3
"""
Unit tests for the client.GithubOrgClient class.
"""

import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from client import GithubOrgClient # Assuming client.py is in the project root
from typing import Dict, Any # Ensure Dict and Any are imported for type hints


class TestGithubOrgClient(unittest.TestCase):
    """
    Tests for the GithubOrgClient class.
    """

    @parameterized.expand([
        ("google", {"login": "google", "id": 123}), # Parametrized test case for 'google'
        ("abc", {"login": "abc", "id": 456}),       # Parametrized test case for 'abc'
    ])
    @patch('client.get_json')  # Patches 'get_json' from the 'client' module's namespace
    def test_org(self, org_name: str, test_payload: Dict, mock_get_json: Mock):
        """
        Tests that GithubOrgClient.org returns the correct value.
        Mocks get_json to prevent external HTTP calls.
        """
        # Configure the mock to return the predefined test_payload
        mock_get_json.return_value = test_payload

        # Instantiate GithubOrgClient with the current parameterized org_name
        client = GithubOrgClient(org_name)

        # Call the .org method of the client instance
        result = client.org()

        # Assertions:
        # 1. Verify that get_json was called exactly once with the expected URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

        # 2. Verify that the output of GithubOrgClient.org matches the test_payload
        self.assertEqual(result, test_payload)
