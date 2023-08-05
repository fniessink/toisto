"""Unit tests for the tools module."""

import unittest

from toisto.tools import first


class FirstTest(unittest.TestCase):
    """Unit tests for the first function."""

    def test_first(self):
        """Test that the first item is returned."""
        self.assertEqual("first", first(["first", "second"]))

    def test_first_with_filter(self):
        """Test that the first item that matches the filter is returned."""
        self.assertEqual("second", first(["first", "second"], lambda item: item.startswith("s")))

    def test_empty_sequence(self):
        """Test that StopIteration is thrown when the sequence is empty."""
        self.assertRaises(StopIteration, first, [])
