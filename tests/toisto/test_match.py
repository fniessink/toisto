"""Unit tests for the matching of answers."""

import unittest

from toisto.match import match


class MatchTest(unittest.TestCase):
    """Unit tests for the match function."""

    def test_equal(self):
        """Test that equal strings match."""
        self.assertTrue(match("foo", "foo"))
        self.assertTrue(match("Foo", "Foo"))
        self.assertTrue(match("foo?", "foo?"))
        self.assertTrue(match("opa's", "opa's"))
        self.assertTrue(match("chocolade-ijs", "chocolade-ijs"))

    def test_do_not_ignore_case(self):
        """Test that case is not ignored."""
        self.assertTrue(match("Foo", "Foo"))
        self.assertFalse(match("foo", "Foo"))
        self.assertTrue(match("FOO", "Foo", "FOO"))
        self.assertFalse(match("foO", "Foo", "FOO"))

    def test_ignore_case(self):
        """Test that case can be ignored."""
        self.assertTrue(match("Foo", "Foo", case_sensitive=False))
        self.assertTrue(match("foo", "Foo", case_sensitive=False))
        self.assertTrue(match("FOO", "Foo", "FOO", case_sensitive=False))
        self.assertTrue(match("foO", "Foo", "FOO", case_sensitive=False))

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

    def test_match_apostrophe(self):
        """Test that an apostrophe cannot be left out."""
        self.assertFalse(match("opa's", "opas"))

    def test_match_hyphen(self):
        """Test that a hyphen cannot be left out."""
        self.assertFalse(match("chocolade-ijs", "chocoladeijs"))
