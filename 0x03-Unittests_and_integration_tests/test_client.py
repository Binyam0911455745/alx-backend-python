#!/usr/bin/env python3
"""
Unit tests for the client.GithubOrgClient class.
"""

import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient
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
    def test_public_repos(self, mock_get_json: Mock):
        """
        Tests GithubOrgClient.public_repos by mocking get_json and
        _public_repos_url. Verifies correct calls and returned data.
        """
        test_repos_payload: List[Dict[str, Any]] = [
            {"name": "alx-backend", "license": {"key": "mit"}},
            {"name": "alx-frontend", "license": {"key": "apache-2.0"}},
            {"name": "alx-fullstack", "license": {"key": "gpl-3.0"}}
        ]
        mock_get_json.return_value = test_repos_payload

        expected_repos_api_url = (
            "https://api.github.com/orgs/mock_org/repos"
        )

        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = expected_repos_api_url

            client = GithubOrgClient("mock_org")
            result = client.public_repos

            self.assertEqual(result, test_repos_payload)
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(expected_repos_api_url)

    # New test method for Task 7: test_has_license
    @parameterized.expand([
        # Test case 1: License matches
        ({"license": {"key": "my_license"}}, "my_license", True),
        # Test case 2: License does not match
        ({"license": {"key": "other_license"}}, "my_license", False),
        # Test case 3: Repo has no license key
        ({"license": {"key": "my_license"}}, "other_license", False),
        # Test case 4: Repo has a license, but its value is None
        ({"license": None}, "my_license", False),
        # Test case 5: Repo has no "license" key at all
        ({}, "my_license", False),
        # Test case 6: More complex repo structure
        ({"name": "test-repo", "license": {"key": "my_license", "name": "MIT"}},
         "my_license", True),
        # Test case 7: Empty license dict
        ({"license": {}}, "my_license", False),
    ])
    def test_has_license(self, repo: Dict[str, Any], license_key: str, expected_result: bool):
        """
        Tests that GithubOrgClient.has_license returns the expected boolean value.
        """
        # Call the static method directly on the class
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected_result)
