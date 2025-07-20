#!/usr/bin/env python3
"""
Utilities for web interactions.
"""
import requests
from typing import Callable, Any
import functools # Import functools for functools.wraps

def get_json(url: str) -> dict:
    """
    Fetches JSON data from a given URL.
    Raises HTTPError for bad responses.
    """
    response = requests.get(url)
    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
    return response.json()


def memoize(fn: Callable) -> Callable:
    """
    Decorator to memoize (cache) the result of a method call.
    """
    attr_name = '_memoized_value_' + fn.__name__

    @functools.wraps(fn) # Use functools.wraps to preserve original function metadata
    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return wrapper