"""Unit tests for concepts."""

from toisto.model.language.concept import Concept, ConceptId
from toisto.model.language.label import Label

from ....base import ToistoTestCase


class ConceptTest(ToistoTestCase):
    """Unit tests for the Concept class."""

    def test_defaults(self):
        """Test the default attributes of a concept."""
        concept = self.create_concept("concept_id", {})
        self.assertEqual("concept_id", concept.concept_id)
        self.assertEqual((), concept.labels(self.fi))
        self.assertEqual((), concept.meanings(self.fi))
        self.assertEqual((), concept.answers)
        self.assertFalse(concept.answer_only)
        self.assertEqual((), concept.roots(self.fi))
        self.assertEqual((), concept.compounds(self.fi))
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
        concept = self.create_concept("thirty", dict(fi="kolmekymmentä", nl="dertig"))
        self.assertEqual(concept, Concept.instances[ConceptId("thirty")])

    def test_meaning_leaf_concept(self):
        """Test the meaning of a leaf concept."""
        concept = self.create_concept("one", dict(fi="yksi", nl="een"))
        self.assertEqual((Label(self.fi, "yksi"),), concept.meanings(self.fi))
        self.assertEqual((Label(self.nl, "een"),), concept.meanings(self.nl))
        self.assertEqual((), concept.meanings(self.en))

    def test_meaning_composite_concept(self):
        """Test the meaning of a composite concept."""
        concept = self.create_concept(
            "table",
            dict(singular=dict(en="table", nl="de tafel"), plural=dict(en="tables", nl="de tafels")),
        )
        self.assertEqual((Label(self.en, "table"), Label(self.en, "tables")), concept.meanings(self.en))
        self.assertEqual((Label(self.nl, "de tafel"), Label(self.nl, "de tafels")), concept.meanings(self.nl))
        self.assertEqual((), concept.meanings(self.fi))

    def test_meaning_mixed_concept(self):
        """Test the meaning of a concept that is leaf in one language and composite in another."""
        concept = self.create_concept(
            "to eat/third person",
            dict(fi="hän syö", female=dict(nl="zij eet"), male=dict(nl="hij eet")),
        )
        self.assertEqual((Label(self.fi, "hän syö"),), concept.meanings(self.fi))
        self.assertEqual((Label(self.nl, "zij eet"), Label(self.nl, "hij eet")), concept.meanings(self.nl))
        self.assertEqual((), concept.meanings(self.en))
