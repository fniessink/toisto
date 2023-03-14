"""Unit tests for the diff methods."""

import unittest

from toisto.ui.dictionary import linkify
from toisto.ui.diff import colored_diff


class DiffTest(unittest.TestCase):
    """Unit tests for colored diffs."""

    def test_equal_strings(self):
        """Test that equal strings have no color."""
        self.assertEqual("foo", colored_diff("foo", "foo"))

    def test_wildly_different_strings(self):
        """Test that wildly different strings are green."""
        self.assertEqual(f"[inserted]{linkify('different')}[/inserted]", colored_diff("completely", "different"))

    def test_text_deleted(self):
        """Test that deleted parts are red."""
        self.assertEqual("fo[deleted]o[/deleted]", colored_diff("foo", "fo"))

    def test_text_added(self):
        """Test that added parts are green."""
        self.assertEqual("foo[inserted]d[/inserted]", colored_diff("foo", "food"))

    def test_text_replaced(self):
        """Test that replaced parts are red and green."""
        self.assertEqual("[deleted]f[/deleted][inserted]g[/inserted]ood", colored_diff("food", "good"))

    def test_text_replaced_case(self):
        """Test that replaced parts are not colored if only the case differs."""
        self.assertEqual("Food", colored_diff("food", "Food"))

    def test_text_replaced_case_and_other_change(self):
        """Test that replaced parts are not colored if only the case differs."""
        self.assertEqual("Foo[deleted]d[/deleted][inserted]t[/inserted]", colored_diff("food", "Foot"))

    def test_text_replaced_long(self):
        """Test that replaced parts with multiple characters are only green."""
        self.assertEqual("gr[inserted]oo[/inserted]t", colored_diff("great", "groot"))
        self.assertEqual("grea[inserted]aa[/inserted]t", colored_diff("great", "greaaat"))

    def test_make_deleted_whitespace_visible(self):
        """Test that deleted whitespace is made visible."""
        expected_diff = "[inserted]Goe[/inserted]de[deleted]_[/deleted]morgen"
        self.assertEqual(expected_diff, colored_diff("de morgen", "Goedemorgen"))

    def test_make_inserted_whitespace_not_visible(self):
        """Test that inserted whitespace is not made visible."""
        self.assertEqual(f"[inserted]{linkify('de morgen')}[/inserted]", colored_diff("uhm", "de morgen"))
