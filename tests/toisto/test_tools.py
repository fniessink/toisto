"""Unit tests for the tools module."""

import unittest

from toisto.tools import first, first_upper


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


class FirstUpperTest(unittest.TestCase):
    """Unit tests for the first_upper function."""

    def test_empty_string(self):
        """Test an empty string."""
        self.assertEqual("", first_upper(""))

    def test_single_charqcter(self):
        """Test single characters."""
        self.assertEqual("A", first_upper("a"))
        self.assertEqual("B", first_upper("B"))

    def test_non_empty_string(self):
        """Test non-empty strings."""
        self.assertEqual("Unchanged", first_upper("Unchanged"))
        self.assertEqual("Upper case, Upper case", first_upper("upper case, Upper case"))
