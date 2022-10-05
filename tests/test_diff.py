"""Unit tests for the diff methods."""

import unittest

from toisto.diff import colored_diff, GREEN, RED, WHITE


class DiffTest(unittest.TestCase):
    """Unit tests for colored diffs."""

    def test_equal_strings(self):
        """Test that equal strings have no color."""
        self.assertEqual("foo", colored_diff("foo", "foo"))

    def test_widly_different_strings(self):
        """Test that wildly different strings are green."""
        self.assertEqual(f"{GREEN}different{WHITE}", colored_diff("completely", "different"))

    def test_text_deleted(self):
        """Test that deleted parts are red."""
        self.assertEqual(f"fo{RED}o{WHITE}", colored_diff("foo", "fo"))

    def test_text_added(self):
        """Test that added parts are green."""
        self.assertEqual(f"foo{GREEN}d{WHITE}", colored_diff("foo", "food"))

    def test_text_replaced(self):
        """Test that replaced parts are red and green."""
        self.assertEqual(f"{RED}f{WHITE}{GREEN}g{WHITE}ood", colored_diff("food", "good"))

    def test_text_replaced_case(self):
        """Test that replaced parts are not colored if only the case differs."""
        self.assertEqual("Food", colored_diff("food", "Food"))

    def test_text_replaced_case_and_other_change(self):
        """Test that replaced parts are not colored if only the case differs."""
        self.assertEqual(f"Foo{RED}d{WHITE}{GREEN}t{WHITE}", colored_diff("food", "Foot"))

    def test_text_replaced_long(self):
        """Test that replaced parts with multiple characters are only green."""
        self.assertEqual(f"gr{GREEN}oo{WHITE}t", colored_diff("great", "groot"))
        self.assertEqual(f"grea{GREEN}aa{WHITE}t", colored_diff("great", "greaaat"))
