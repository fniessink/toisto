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
            "morning",
            dict(singular=dict(fi="Aamu", nl="De ochtend"), plural=dict(fi="Aamut", nl="De ochtenden")),
        )
        self.assertEqual(2, len(concept.constituent_concepts))

    def test_uses(self):
        """Test that a concept can have a uses relation with another concept."""
        concept = self.create_concept("mall", dict(uses=["shop", "centre"], fi="Kauppakeskus", nl="Het winkelcentrum"))
        self.assertEqual(("shop", "centre"), concept.used_concepts("fi"))

    def test_language_specific_uses(self):
        """Test that a concept can have a uses relation with another concept in one language but not in another."""
        concept = self.create_concept("decade", dict(uses=dict(fi="year"), fi="Vuosikymmen", en="Decade"))
        self.assertEqual(("year",), concept.used_concepts("fi"))
        self.assertEqual((), concept.used_concepts("en"))

    def test_opposite(self):
        """Test that a concept can have an opposite relation with another concept."""
        concept = self.create_concept("big", dict(opposite="small", en="Big"))
        self.assertEqual(("small",), concept.opposite_concepts)

    def test_multiple_opposites(self):
        """Test that a concept can have multiple opposites."""
        concept = self.create_concept("big", dict(opposite=["small", "little"], en="Big"))
        self.assertEqual(("small", "little"), concept.opposite_concepts)

    def test_opposites_of_composite(self):
        """Test that a composite concepts can have an opposite."""
        concept = self.create_concept(
            "big",
            {
                "opposite": "small",
                "positive degree": dict(en="Big"),
                "comparative degree": dict(en="Bigger"),
                "superlative degree": dict(en="Biggest"),
            },
        )
        self.assertEqual(("small",), concept.opposite_concepts)
        for index, degree in enumerate(["positive", "comparative", "superlative"]):
            self.assertEqual((f"small/{degree} degree",), concept.constituent_concepts[index].opposite_concepts)

    def test_level(self):
        """Test that a concept can have a level."""
        concept = self.create_concept("one", dict(level=dict(A1="EP"), fi="Yksi", nl="Eén"))
        self.assertEqual("A1", concept.level)

    def test_override_level(self):
        """Test that constituent concepts can override the level of their composite concept."""
        concept = self.create_concept(
            "morning",
            dict(
                level=dict(A1="EP"),
                singular=dict(fi="Aamu", nl="De ochtend"),
                plural=dict(level=dict(A2="EP"), fi="Aamut", nl="De ochtenden"),
            ),
        )
        self.assertEqual("A1", concept.constituent_concepts[0].level)
        self.assertEqual("A2", concept.constituent_concepts[1].level)

    def test_missing_level(self):
        """Test that the concept has no level if the concept dict does not contain one."""
        concept = self.create_concept("one", dict(level=dict(none="EP"), fi="Yksi", nl="Eén"))
        self.assertEqual(None, concept.level)
