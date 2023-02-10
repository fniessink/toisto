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

    def test_antonym(self):
        """Test that a concept can have an antonym concept."""
        big = self.create_concept("big", dict(antonym="small", en="Big"))
        small = self.create_concept("small", dict(en="Small"))
        self.assertEqual((small,), big.antonym_concepts)

    def test_multiple_antonyms(self):
        """Test that a concept can have multiple antonyms."""
        big = self.create_concept("big", dict(antonym=["small", "little"], en="Big"))
        little = self.create_concept("little", dict(en="Little"))
        small = self.create_concept("small", dict(en="Small"))
        self.assertEqual((small, little), big.antonym_concepts)

    def test_antonyms_of_composite(self):
        """Test that a composite concept can have an antonym."""
        big = self.create_concept(
            "big",
            {
                "antonym": "small",
                "positive degree": dict(en="Big"),
                "comparative degree": dict(en="Bigger"),
                "superlative degree": dict(en="Biggest"),
            },
        )
        small = self.create_concept(
            "small",
            {
                "positive degree": dict(en="Small"),
                "comparative degree": dict(en="Smaller"),
                "superlative degree": dict(en="Smallest"),
            },
        )
        self.assertEqual((small,), big.antonym_concepts)
        for index in range(3):
            self.assertEqual((small.constituent_concepts[index],), big.constituent_concepts[index].antonym_concepts)

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
