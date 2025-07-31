"""Unit tests for the label factory."""

from typing import cast

from toisto.model.language import EN, NL
from toisto.model.language.concept import ConceptId
from toisto.model.language.grammar import GrammaticalCategory
from toisto.model.language.label import Label
from toisto.model.language.label_factory import LabelFactory, LabelJSON

from ....base import ToistoTestCase


class LabelFactoryTest(ToistoTestCase):
    """Label factory unit tests."""

    def test_create_label(self):
        """Test creating a single label."""
        chair_json: LabelJSON = {"concept": ConceptId("chair"), "label": "chair", "language": EN}
        self.assertEqual((Label(EN, "chair"),), LabelFactory([chair_json]).create_labels())

    def test_create_labels(self):
        """Test creating multiple labels."""
        chair_json: LabelJSON = {"concept": ConceptId("chair"), "label": "chair", "language": EN}
        table_json: LabelJSON = {"concept": ConceptId("table"), "label": "table", "language": EN}
        self.assertEqual(
            (Label(EN, "chair"), Label(EN, "table")), LabelFactory([chair_json, table_json]).create_labels()
        )

    def test_create_label_with_spelling_alternatives(self):
        """Test creating a label with spelling alternatives."""
        color_json: LabelJSON = {"concept": ConceptId("color"), "label": ["color", "colour"], "language": EN}
        self.assertEqual((Label(EN, ["color", "colour"]),), LabelFactory([color_json]).create_labels())

    def test_create_synonym_labels(self):
        """Test creating synonym labels."""
        begin_json: LabelJSON = {"concept": ConceptId("begin"), "label": "begin", "language": EN}
        start_json: LabelJSON = {"concept": ConceptId("begin"), "label": "start", "language": EN}
        self.assertEqual(
            (Label(EN, "begin", grammatical_base="begin"), Label(EN, "start", grammatical_base="start")),
            LabelFactory([begin_json, start_json]).create_labels(),
        )

    def test_create_label_with_grammatical_forms(self):
        """Test creating labels with grammatical forms."""
        chair_json: LabelJSON = {
            "concept": ConceptId("chair"),
            "label": cast("dict[GrammaticalCategory, str]", {"singular": "chair", "plural": "chairs"}),
            "language": EN,
        }
        self.assertEqual(
            (
                Label(EN, "chair", grammatical_base="chair", grammatical_categories=("singular",)),
                Label(EN, "chairs", grammatical_base="chair", grammatical_categories=("plural",)),
            ),
            LabelFactory([chair_json]).create_labels(),
        )

    def test_create_label_with_nested_grammatical_forms(self):
        """Test creating labels with nested grammatical forms."""
        chair_json: LabelJSON = {
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
        self.assertEqual(
            (
                Label(NL, "de stoel", grammatical_base="de stoel", grammatical_categories=("root", "singular")),
                Label(NL, "de stoelen", grammatical_base="de stoel", grammatical_categories=("root", "plural")),
                Label(
                    NL, "het stoeltje", grammatical_base="de stoel", grammatical_categories=("diminutive", "singular")
                ),
                Label(NL, "de stoeltjes", grammatical_base="de stoel", grammatical_categories=("diminutive", "plural")),
            ),
            LabelFactory([chair_json]).create_labels(),
        )
