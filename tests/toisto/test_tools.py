"""Unit tests for the zip_and_cycle function."""

import unittest

from toisto.tools import first, zip_and_cycle


class ZipAndcycleTest(unittest.TestCase):
    """Unit tests for the zip_and_cycle function."""

    def test_no_lists(self):
        """Test that the function works without arguments."""
        self.assertEqual([], list(zip_and_cycle()))

    def test_one_empty_list(self):
        """Test that the function works with one empty list."""
        self.assertEqual([], list(zip_and_cycle([])))

    def test_two_empty_lists(self):
        """Test that the function works with two empty lists."""
        self.assertEqual([], list(zip_and_cycle([], [])))

    def test_two_equal_length_lists(self):
        """Test that the function works with two equal length lists."""
        self.assertEqual([(1, 2)], list(zip_and_cycle([1], [2])))

    def test_two_different_length_lists(self):
        """Test that the function works with two different length lists."""
        self.assertEqual([(1, 2), (1, 3)], list(zip_and_cycle([1], [2, 3])))

    def test_two_different_length_lists_one_empty(self):
        """Test that the function works with two different length lists."""
        self.assertEqual([], list(zip_and_cycle([], [2, 3])))


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
