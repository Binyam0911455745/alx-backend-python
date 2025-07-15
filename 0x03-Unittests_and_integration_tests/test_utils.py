#!/usr/bin/env python3
"""
Unit tests for access_nested_map function from utils module.
"""

import unittest
from parameterized import parameterized
from utils import access_nested_map


class TestAccessNestedMap(unittest.TestCase):
    """
    Tests for the access_nested_map function.
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected_result):
        """
        Tests that access_nested_map returns the expected result.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected_result)

    @parameterized.expand([
        ({}, ("a",), "a"),  # nested_map, path, expected_key_in_exception
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key):
        """
        Tests that access_nested_map raises a KeyError with the expected message.
        """
        with self.assertRaisesRegex(KeyError, f"'{expected_key}'"):
            access_nested_map(nested_map, path)



