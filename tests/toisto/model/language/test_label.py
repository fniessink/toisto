"""Unit tests for labels."""

import unittest

from toisto.model.language.label import Label


class LabelTest(unittest.TestCase):
    """Unit tests for the Label class."""

    def test_equality(self):
        """Test that labels are not equal to non-labels."""
        label = Label("en", "English")
        equal_to_object = label == object()
        self.assertFalse(equal_to_object)
        not_equal_to_object = label != object()
        self.assertTrue(not_equal_to_object)
