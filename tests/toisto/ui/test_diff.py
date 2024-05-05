"""Unit tests for the diff methods."""

import unittest

from toisto.ui.dictionary import linkified
from toisto.ui.diff import colored_diff
from toisto.ui.style import DELETED, INSERTED


class DiffTest(unittest.TestCase):
    """Unit tests for colored diffs."""

    def test_equal_strings(self):
        """Test that equal strings have no color."""
        self.assertEqual("foo", colored_diff("foo", "foo"))

    def test_wildly_different_strings(self):
        """Test that wildly different strings are green."""
        self.assertEqual(f"[{INSERTED}]{linkified('different')}[/{INSERTED}]", colored_diff("completely", "different"))

    def test_text_deleted(self):
        """Test that deleted parts are red."""
        self.assertEqual(f"fo[{DELETED}]o[/{DELETED}]", colored_diff("foo", "fo"))

    def test_text_added(self):
        """Test that added parts are green."""
        self.assertEqual(f"foo[{INSERTED}]d[/{INSERTED}]", colored_diff("foo", "food"))

    def test_text_replaced(self):
        """Test that replaced parts are red and green."""
        self.assertEqual(f"[{DELETED}]f[/{DELETED}][{INSERTED}]g[/{INSERTED}]ood", colored_diff("food", "good"))

    def test_text_replaced_case(self):
        """Test that replaced parts are not colored if only the case differs."""
        self.assertEqual("Food", colored_diff("food", "Food"))

    def test_text_replaced_case_and_other_change(self):
        """Test that replaced parts are not colored if only the case differs."""
        self.assertEqual(f"Foo[{DELETED}]d[/{DELETED}][{INSERTED}]t[/{INSERTED}]", colored_diff("food", "Foot"))

    def test_text_replaced_long(self):
        """Test that replaced parts with multiple characters are only green."""
        self.assertEqual(f"gr[{INSERTED}]oo[/{INSERTED}]t", colored_diff("great", "groot"))
        self.assertEqual(f"grea[{INSERTED}]aa[/{INSERTED}]t", colored_diff("great", "greaaat"))

    def test_make_deleted_whitespace_visible(self):
        """Test that deleted whitespace is made visible."""
        expected_diff = f"[{INSERTED}]Goe[/{INSERTED}]de[{DELETED}]_[/{DELETED}]morgen"
        self.assertEqual(expected_diff, colored_diff("de morgen", "Goedemorgen"))

    def test_make_inserted_whitespace_not_visible(self):
        """Test that inserted whitespace is not made visible."""
        self.assertEqual(f"[{INSERTED}]{linkified('de morgen')}[/{INSERTED}]", colored_diff("uhm", "de morgen"))
