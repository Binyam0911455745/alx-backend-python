#!/usr/bin/env python3
"""
Unit tests for access_nested_map and get_json functions from utils module.
"""

import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json # Import get_json
from typing import Dict, List, Any, Sequence, Callable, Mapping # Add these imports



class TestAccessNestedMap(unittest.TestCase):
    """
    Tests for the access_nested_map function.
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path: Sequence expected_result:Any):
        """
        Tests that access_nested_map returns the expected result.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected_result)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path:  Sequence, expected_key: str):
        """
        Tests that access_nested_map raises a KeyError with the expected message.
        """
        with self.assertRaisesRegex(KeyError, f"'{expected_key}'"):
            access_nested_map(nested_map, path)


class TestGetJson(unittest.TestCase):
    """
    Tests for the get_json function.
    """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('requests.get') # This patches requests.get for the duration of this test method
    def test_get_json(self, test_url: str, test_payload: Dict, mock_get: Mock):
        """
        Tests that get_json returns the expected result and mocks HTTP calls.
        """
        # Configure the mock object:
        # mock_get is a Mock object representing requests.get
        # We want mock_get to return another Mock object when called
        # This returned Mock object should have a .json() method
        # The .json() method should return test_payload
        mock_get.return_value = Mock()
        mock_get.return_value.json.return_value = test_payload

        # Call the function under test
        result = get_json(test_url)

        # Assertions
        # 1. Test that the mocked get method was called exactly once with test_url
        mock_get.assert_called_once_with(test_url)

        # 2. Test that the output of get_json is equal to test_payload
        self.assertEqual(result, test_payload)
