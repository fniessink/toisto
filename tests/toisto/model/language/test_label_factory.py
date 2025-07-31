"""Unit tests for the label factory."""

from toisto.model.language import EN
from toisto.model.language.concept import ConceptId
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
