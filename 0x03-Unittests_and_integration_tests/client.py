#!/usr/bin/env python3
"""
A client for interacting with the GitHub API.
"""

import requests
from typing import Dict, Any
from utils import get_json

class GithubOrgClient:
    """
    Client for the GitHub organization API.
    """
    def __init__(self, org_name: str) -> None:
        """Initializes the GithubOrgClient with an organization name."""
        self._org_name = org_name
        self._repos_payload = None

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
    def org(self) -> dict:
        """
        Returns the organization's public information.
        This method makes an API call to get_json.
        """
        org_url = f"https://api.github.com/orgs/{self._org_name}"
        return get_json(org_url)
    @property
    def _public_repos_url(self) -> str:
        """
        Returns the URL to list public repositories of the organization.
        It extracts this from the org payload.
        """
        org_data = self.org()
        return org_data["repos_url"]
    
    @property
    def public_repos(self) -> list:
        """
        Returns the list of public repositories for the organization.
        This method uses _public_repos_url and caches the result.
        """
        if self._repos_payload is None:
            repos_url = self._public_repos_url
            self._repos_payload = get_json(repos_url)
        return self._repos_payload
      
    @staticmethod
    def has_license(repo: Dict[str, Any], license_key: str) -> bool:
        """
        Checks if a repository has a specific license key.
        """
        if not isinstance(repo, dict) or 'license' not in repo or \
                not isinstance(repo['license'], dict):
            return False
        return repo['license'].get('key') == license_key   

    # Note: Other methods like repos_url, public_repos, has_public_repo
    # will be added in later tasks if required.