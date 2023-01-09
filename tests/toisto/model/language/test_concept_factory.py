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
