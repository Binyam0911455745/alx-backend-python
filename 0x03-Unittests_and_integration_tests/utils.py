#!/usr/bin/env python3
"""
Utilities for web interactions and nested data access.
"""
import requests
import functools
from typing import Mapping, Sequence, Any, Callable


def access_nested_map(nested_map: Mapping, path: Sequence) -> Any:
    """
    Accesses a value in a nested dictionary using a sequence of keys.
    """
    current_map = nested_map
    for key in path:
        if not isinstance(current_map, Mapping) or key not in current_map:
            raise KeyError(f"'{key}'")
        current_map = current_map[key]
    return current_map


def get_json(url: str) -> dict:
    """
    Fetches JSON data from a given URL.
    Raises HTTPError for bad responses.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def memoize(fn: Callable) -> Callable:
    """
    Decorator to memoize (cache) the result of a method call.
    """
    attr_name = '_memoized_value_' + fn.__name__

    @functools.wraps(fn)
    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return wrapper