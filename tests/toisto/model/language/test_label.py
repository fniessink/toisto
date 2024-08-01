"""Unit tests for labels."""

from toisto.model.language import EN, FI, NL
from toisto.model.language.label import Label, Labels

from ....base import ToistoTestCase


class LabelTest(ToistoTestCase):
    """Unit tests for the Label class."""

    def test_equality(self):
        """Test that labels are not equal to non-labels."""
        label = Label(EN, "English")
        equal_to_object = label == object()
        self.assertFalse(equal_to_object)
        not_equal_to_object = label != object()
        self.assertTrue(not_equal_to_object)

    def test_complete_sentence(self):
        """Test that a colloquial sentence is recognized."""
        label = Label(FI, "Kiitti!*")
        self.assertTrue(label.is_complete_sentence)

    def test_repr(self):
        """Test the representation of a label."""
        self.assertEqual("English", repr(Label(EN, "English")))


class LabelsTest(ToistoTestCase):
    """Unit tests for the Labels class."""

    def test_repr(self):
        """Test the representation of multiple labels."""
        self.assertEqual("('English', 'Nederlands')", repr(Labels([Label(EN, "English"), Label(NL, "Nederlands")])))
