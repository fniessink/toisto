"""Unit tests for labels."""

from toisto.model.language.label import Label

from ....base import ToistoTestCase


class LabelTest(ToistoTestCase):
    """Unit tests for the Label class."""

    def test_equality(self):
        """Test that labels are not equal to non-labels."""
        label = Label(self.en, "English")
        equal_to_object = label == object()
        self.assertFalse(equal_to_object)
        not_equal_to_object = label != object()
        self.assertTrue(not_equal_to_object)
