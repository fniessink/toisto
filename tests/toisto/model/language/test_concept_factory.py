"""Concept factory unit tests."""

from ...base import ToistoTestCase


class ConcepFactoryTest(ToistoTestCase):
    """Unit tests for the concept factory class."""

    def test_leaf_concept(self):
        """Test that a leaf concept has no constituent concepts."""
        concept = self.create_concept("english", dict(en=["English"], nl=["Engels"]))
        self.assertEqual((), concept.constituent_concepts)

    def test_composite_concept(self):
        """Test that a composite concept has constituent concepts."""
        concept = self.create_concept(
            "morning", dict(singular=dict(fi="Aamu", nl="De ochtend"), plural=dict(fi="Aamut", nl="De ochtenden"))
        )
        self.assertEqual(2, len(concept.constituent_concepts))

    def test_uses(self):
        """Test that a concept can have a uses relation with another concept."""
        concept = self.create_concept("mall", dict(uses=["shop", "centre"], fi="Kauppakeskus", nl="Het winkelcentrum"))
        self.assertEqual(("shop", "centre"), concept.uses)

    def test_plural_auto_uses_singular(self):
        """Test that a plural concept automatically has a uses relation with the singular concept."""
        concept = self.create_concept(
            "morning", dict(singular=dict(fi="Aamu", nl="De ochtend"), plural=dict(fi="Aamut", nl="De ochtenden"))
        )
        self.assertEqual(("morning/singular",), concept.constituent_concepts[1].uses)

    def test_past_tense_auto_uses_present_tense(self):
        """Test that a past tense concept automatically has a uses relation with the present tense concept."""
        concept = self.create_concept(
            "to eat", {"present tense": dict(en="I eat", nl="Ik eet"), "past tense": dict(en="I ate", nl="Ik at")}
        )
        self.assertEqual(("to eat/present tense",), concept.constituent_concepts[1].uses)

    def test_negation_auto_uses_affirmation(self):
        """Test that a negative concept automatically has a uses relation with the affirmative concept."""
        concept = self.create_concept(
            "to eat", dict(affirmative=dict(en="I eat", nl="Ik eet"), negative=dict(en="I don't eat", nl="Ik eet niet"))
        )
        self.assertEqual(("to eat/affirmative",), concept.constituent_concepts[1].uses)
