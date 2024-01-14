"""Unit tests for concepts."""

from toisto.model.language.concept import Concept
from toisto.model.language.concept_factory import create_concept
from toisto.model.language.label import Label

from ....base import ToistoTestCase


class ConceptTest(ToistoTestCase):
    """Unit tests for the Concept class."""

    def test_defaults(self):
        """Test the default attributes of a concept."""
        concept = create_concept("concept_id", {})
        self.assertEqual("concept_id", concept.concept_id)
        self.assertEqual((), concept.labels("fi"))
        self.assertEqual((), concept.meanings("fi"))
        self.assertEqual((), concept.answers)
        self.assertFalse(concept.answer_only)
        self.assertEqual((), concept.roots("fi"))
        self.assertEqual((), concept.compounds("fi"))
        self.assertIsNone(concept.parent)
        self.assertEqual((), concept.constituents)
        self.assertEqual((), concept.antonyms)
        self.assertEqual((), concept.hypernyms)
        self.assertEqual((), concept.hyponyms)
        self.assertEqual((), concept.holonyms)
        self.assertEqual((), concept.meronyms)
        self.assertEqual((), concept.involves)
        self.assertEqual((), concept.involved_by)

    def test_instance_registry(self):
        """Test that concepts register themselves with the Concept class instance registry."""
        concept = create_concept("thirty", dict(fi="kolmekymmentä", nl="dertig"))
        self.assertEqual(concept, Concept.instances["thirty"])

    def test_meaning_leaf_concept(self):
        """Test the meaning of a leaf concept."""
        concept = create_concept("one", dict(fi="yksi", nl="een"))
        self.assertEqual((Label("fi", "yksi"),), concept.meanings("fi"))
        self.assertEqual((Label("nl", "een"),), concept.meanings("nl"))
        self.assertEqual((), concept.meanings("en"))

    def test_meaning_composite_concept(self):
        """Test the meaning of a composite concept."""
        concept = create_concept(
            "table",
            dict(singular=dict(en="table", nl="de tafel"), plural=dict(en="tables", nl="de tafels")),
        )
        self.assertEqual((Label("en", "table"), Label("en", "tables")), concept.meanings("en"))
        self.assertEqual((Label("nl", "de tafel"), Label("nl", "de tafels")), concept.meanings("nl"))
        self.assertEqual((), concept.meanings("fi"))

    def test_meaning_mixed_concept(self):
        """Test the meaning of a concept that is leaf in one language and composite in another."""
        concept = create_concept(
            "to eat/third person",
            dict(fi="hän syö", female=dict(nl="zij eet"), male=dict(nl="hij eet")),
        )
        self.assertEqual((Label("fi", "hän syö"),), concept.meanings("fi"))
        self.assertEqual((Label("nl", "zij eet"), Label("nl", "hij eet")), concept.meanings("nl"))
        self.assertEqual((), concept.meanings("en"))
