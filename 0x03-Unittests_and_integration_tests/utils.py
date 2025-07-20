#!/usr/bin/env python3
"""
Utility functions for nested map access, JSON fetching, and memoization.
"""

import requests
from typing import Mapping, Sequence, Any, Dict, Callable

def access_nested_map(nested_map: Mapping, path: Sequence) -> Any:
    """
    Accesses a value in a nested dictionary or list using a sequence of keys/indices.

    Args:
        nested_map (Mapping): The nested dictionary or list to traverse.
        path (Sequence): A sequence of keys or indices representing the path
                         to the desired value.

    Returns:
        Any: The value found at the specified path.

    Raises:
        KeyError: If any key in the path does not exist in the nested map.
    """
    current_map = nested_map
    for key in path:
        if not isinstance(current_map, Mapping) or key not in current_map:
            raise KeyError(key)
        current_map = current_map[key]
    return current_map

def get_json(url: str) -> Dict:
    """
    Fetches JSON data from a given URL.

    Args:
        url (str): The URL to fetch JSON from.

    Returns:
        Dict: The JSON response as a dictionary.

    Raises:
        requests.exceptions.RequestException: If the HTTP request fails.
    """
    response = requests.get(url)
    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
    return response.json()

def memoize(fn: Callable) -> Callable:
    """
    A decorator that memoizes the result of a method call.
    It caches the result of the first call and returns the cached result for subsequent calls.
    """
    attr_name = '_memoized_value_' + fn.__name__

    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return wrapper