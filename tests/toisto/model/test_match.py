"""Unit tests for the matching of answers."""

import unittest

from toisto.model.match import match


class MatchTest(unittest.TestCase):
    """Unit tests for the match function."""

    def test_equal(self):
        """Test that equal strings match."""
        self.assertTrue(match("foo", "foo"))

    def test_ignore_case(self):
        """Test that case is ignored."""
        self.assertTrue(match("foo", "FoO"))

    def test_ignore_punctuation(self):
        """Test that punctuation is ignored."""
        self.assertTrue(match("foo?", "foo!"))

    def test_do_not_ignore_accents(self):
        """Test that accents are not ignored."""
        self.assertFalse(match("foö", "foo"))

    def test_strip_whitespace(self):
        """Test that whitespace is ignored."""
        self.assertTrue(match("foo ", "\tfoo"))

    def test_match_none_of_many(self):
        """Test that the text can be matched against multiple texts."""
        self.assertFalse(match("foö", "foo", "fool"))

    def test_match_one_of_many(self):
        """Test that the text can be matched against multiple texts."""
        self.assertTrue(match("foo", "foo", "fool", "fools"))
