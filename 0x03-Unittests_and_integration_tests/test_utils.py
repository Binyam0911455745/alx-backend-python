#!/usr/bin/env python3
"""
Unit tests for access_nested_map, get_json functions, and memoize decorator from utils module.
"""

import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize # Make sure memoize is imported
from typing import Dict, List, Any, Sequence, Callable, Mapping # Crucial for resolving NameError: name 'Dict' is not defined


class TestAccessNestedMap(unittest.TestCase):
    """
    Tests for the access_nested_map function.
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map: Mapping, path: Sequence, expected_result: Any):
        """
        Tests that access_nested_map returns the expected result.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected_result)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map: Mapping, path: Sequence, expected_key: str):
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
    @patch('requests.get')
    def test_get_json(self, test_url: str, test_payload: Dict, mock_get: Mock):
        """
        Tests that get_json returns the expected result and mocks HTTP calls.
        """
        mock_get.return_value = Mock()
        mock_get.return_value.json.return_value = test_payload

        result = get_json(test_url)

        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """
    Tests for the memoize decorator.
    """
    def test_memoize(self):
        """
        Tests that memoize caches the result of a method call.
        """
        class TestClass:
            # We will patch this method
            def a_method(self):
                """A simple method that returns 42."""
                return 42

            @memoize # This will make a_property a memoized property
            def a_property(self):
                """A memoized property that calls a_method."""
                return self.a_method()

        # Patch 'a_method' inside 'TestClass'
        with patch.object(TestClass, 'a_method', return_value=42) as mock_a_method:
            test_instance = TestClass()

            # Call a_property twice
            # As per the task, calling it like a property (without ())
            result1 = test_instance.a_property
            result2 = test_instance.a_property

            # Assertions
            # 1. Test that a_method was called exactly once
            mock_a_method.assert_called_once()

            # 2. Test that the correct result is returned
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)

