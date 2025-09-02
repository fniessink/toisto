"""Unit tests for grammar."""

from toisto.model.language.grammatical_form import GrammaticalForm

from ....base import ToistoTestCase


class GrammaticalFormTest(ToistoTestCase):
    """Unit tests for the GrammaticalForm class."""

    def test_equality_to_self(self):
        """Test that grammatical forms are not equal to non-labels."""
        grammatical_form = same_grammatical_form = GrammaticalForm("table", "singular")
        forms_equal = grammatical_form == same_grammatical_form
        self.assertTrue(forms_equal)
        forms_not_equal = grammatical_form != same_grammatical_form
        self.assertFalse(forms_not_equal)

    def test_equality_to_object(self):
        """Test that grammatical forms are not equal to other types."""
        grammatical_form = GrammaticalForm()
        equal_to_object = grammatical_form == object()
        self.assertFalse(equal_to_object)
        not_equal_to_object = grammatical_form != object()
        self.assertTrue(not_equal_to_object)

    def test_hash(self):
        """Test that grammatical forms can be used as dict keys."""
        form_dict: dict[GrammaticalForm, str] = {}
        form_dict[GrammaticalForm()] = "default grammatical form"
        self.assertEqual("default grammatical form", form_dict[GrammaticalForm()])

    def test_grammatical_differences(self):
        """Test the grammatical differences between two grammatical forms."""
        default = GrammaticalForm()
        self.assertEqual(set(), default.grammatical_differences(default))
        singular = GrammaticalForm("", "singular")
        plural = GrammaticalForm("", "plural")
        self.assertEqual(set(), singular.grammatical_differences(default))
        self.assertEqual({"plural"}, default.grammatical_differences(plural))
        self.assertEqual({"plural"}, singular.grammatical_differences(plural))
        first_person_singular = GrammaticalForm("", "singular", "first person")
        self.assertEqual({"first person"}, singular.grammatical_differences(first_person_singular))
        self.assertEqual(set(), first_person_singular.grammatical_differences(singular))
        self.assertEqual({"plural"}, first_person_singular.grammatical_differences(plural))
