"""Unit tests for the label factory."""

from typing import TYPE_CHECKING, cast

from toisto.model.language import EN, NL
from toisto.model.language.concept import ConceptId
from toisto.model.language.grammar import GrammaticalForm
from toisto.model.language.label import Label
from toisto.model.language.label_factory import LabelFactory, LabelJSON

from ....base import ToistoTestCase

if TYPE_CHECKING:
    from toisto.model.language.grammar import GrammaticalCategory


class LabelFactoryTest(ToistoTestCase):
    """Label factory unit tests."""

    def label(self, label: str, concept_id: str = "") -> LabelJSON:
        """Create a simple label."""
        return {"concept": ConceptId(concept_id or label), "label": label, "language": EN}

    def label_with_spelling_alternatives(self) -> LabelJSON:
        """Create a label with multiple spelling alternatives."""
        return {"concept": ConceptId("color"), "label": ["color", "colour"], "language": EN}

    def label_with_grammatical_number(self) -> LabelJSON:
        """Create a label with grammatical number forms."""
        return {
            "concept": ConceptId("chair"),
            "label": cast("dict[GrammaticalCategory, str]", {"singular": "chair", "plural": "chairs"}),
            "language": EN,
        }

    def label_with_grammatical_number_and_diminutive(self) -> LabelJSON:
        """Create a label with grammatical number and diminutive forms."""
        return {
            "concept": ConceptId("chair"),
            "label": cast(
                "dict[GrammaticalCategory, dict[GrammaticalCategory, str]]",
                {
                    "root": {"singular": "de stoel", "plural": "de stoelen"},
                    "diminutive": {"singular": "het stoeltje", "plural": "de stoeltjes"},
                },
            ),
            "language": NL,
        }

    def test_create_label(self):
        """Test creating a single label."""
        chair_json = self.label("chair")
        self.assertEqual((Label(EN, "chair"),), LabelFactory().create_labels([chair_json]))

    def test_create_labels(self):
        """Test creating multiple labels."""
        chair_json = self.label("chair")
        table_json = self.label("table")
        self.assertEqual(
            (Label(EN, "chair"), Label(EN, "table")), LabelFactory().create_labels([chair_json, table_json])
        )

    def test_create_label_with_spelling_alternatives(self):
        """Test creating a label with spelling alternatives."""
        color_json = self.label_with_spelling_alternatives()
        self.assertEqual((Label(EN, ["color", "colour"]),), LabelFactory().create_labels([color_json]))

    def test_create_synonym_labels(self):
        """Test creating synonym labels."""
        begin_json = self.label("begin")
        start_json = self.label("start", concept_id="begin")
        self.assertEqual(
            (Label(EN, "begin"), Label(EN, "start")),
            LabelFactory().create_labels([begin_json, start_json]),
        )

    def test_create_label_with_grammatical_forms(self):
        """Test creating labels with grammatical forms."""
        chair_json = self.label_with_grammatical_number()
        self.assertEqual(
            (
                Label(EN, "chair", GrammaticalForm("chair", "singular")),
                Label(EN, "chairs", GrammaticalForm("chair", "plural")),
            ),
            LabelFactory().create_labels([chair_json]),
        )

    def test_create_label_with_nested_grammatical_forms(self):
        """Test creating labels with nested grammatical forms."""
        chair_json = self.label_with_grammatical_number_and_diminutive()
        base = "de stoel"
        self.assertEqual(
            (
                Label(NL, "de stoel", GrammaticalForm(base, "root", "singular")),
                Label(NL, "de stoelen", GrammaticalForm(base, "root", "plural")),
                Label(NL, "het stoeltje", GrammaticalForm(base, "diminutive", "singular")),
                Label(NL, "de stoeltjes", GrammaticalForm(base, "diminutive", "plural")),
            ),
            LabelFactory().create_labels([chair_json]),
        )

    def test_grammatical_base(self):
        """Test the grammatical base of a simple label."""
        chair_json = self.label("chair")
        self.assertEqual("chair", LabelFactory.grammatical_base_for(chair_json))

    def test_grammatical_base_with_spelling_alternatives(self):
        """Test the grammatical base of a label with spelling alternatives."""
        color_json = self.label_with_spelling_alternatives()
        self.assertEqual("color", LabelFactory.grammatical_base_for(color_json))

    def test_grammatical_base_with_grammatical_forms(self):
        """Test the grammatical base of a label with different grammatical forms."""
        chair_json = self.label_with_grammatical_number()
        self.assertEqual("chair", LabelFactory.grammatical_base_for(chair_json))

    def test_grammatical_base_with_nested_grammatical_forms(self):
        """Test the grammatical base of a label with nested grammatical forms."""
        chair_json = self.label_with_grammatical_number_and_diminutive()
        self.assertEqual("de stoel", LabelFactory.grammatical_base_for(chair_json))
