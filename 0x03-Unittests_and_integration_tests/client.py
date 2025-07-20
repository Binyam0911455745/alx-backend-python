#!/usr/bin/env python3
"""
A client for interacting with the GitHub API.
"""

import requests
from typing import Dict, List, Any

class GithubOrgClient:
    """
    Client for the GitHub organization API.
    """
    def __init__(self, org_name: str) -> None:
        """Initializes the GithubOrgClient with an organization name."""
        self._org_name = org_name

    def get_org_data(self) -> Dict:
        """Fetches organization data from GitHub."""
        url = f"https://api.github.com/orgs/{self._org_name}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_public_repos(self) -> List[Dict]:
        """Fetches public repositories for the organization."""
        org_data = self.get_org_data()
        repos_url = org_data["repos_url"]
        response = requests.get(repos_url)
        response.raise_for_status()
        return response.json()

    def has_license(self, repo: Dict, license_key: str) -> bool:
        """Checks if a repository has a specific license."""
        if "license" not in repo or repo["license"] is None:
            return False
        return repo["license"]["key"] == license_key