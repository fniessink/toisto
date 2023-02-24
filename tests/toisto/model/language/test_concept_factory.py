"""Concept factory unit tests."""

from ....base import ToistoTestCase


class ConcepFactoryTest(ToistoTestCase):
    """Unit tests for the concept factory class."""

    def test_leaf_concept(self):
        """Test that a leaf concept has no constituent concepts."""
        concept = self.create_concept("english", dict(en=["English"], nl=["Engels"]))
        self.assertEqual((), concept.constituents)

    def test_composite_concept(self):
        """Test that a composite concept has constituent concepts."""
        concept = self.create_concept(
            "morning",
            dict(singular=dict(fi="Aamu", nl="De ochtend"), plural=dict(fi="Aamut", nl="De ochtenden")),
        )
        self.assertEqual(2, len(concept.constituents))

    def test_roots(self):
        """Test that a concept can have roots."""
        concept = self.create_concept("mall", dict(roots=["shop", "centre"], fi="Kauppakeskus", nl="Het winkelcentrum"))
        shop = self.create_concept("shop", dict(fi="Kauppa"))
        centre = self.create_concept("centre", dict(fi="Keskusta"))
        self.assertEqual((shop, centre), concept.roots("fi"))

    def test_language_specific_roots(self):
        """Test that a concept can have a root in one language but not in another."""
        decade = self.create_concept("decade", dict(roots=dict(fi="year"), fi="Vuosikymmen", en="Decade"))
        year = self.create_concept("year", dict(fi="Vuosi"))
        self.assertEqual((year,), decade.roots("fi"))
        self.assertEqual((), decade.roots("en"))

    def test_antonym(self):
        """Test that a concept can have an antonym concept."""
        big = self.create_concept("big", dict(antonym="small", en="Big"))
        small = self.create_concept("small", dict(en="Small"))
        self.assertEqual((small,), big.antonyms)

    def test_multiple_antonyms(self):
        """Test that a concept can have multiple antonyms."""
        big = self.create_concept("big", dict(antonym=["small", "little"], en="Big"))
        little = self.create_concept("little", dict(en="Little"))
        small = self.create_concept("small", dict(en="Small"))
        self.assertEqual((small, little), big.antonyms)

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
        self.assertEqual((small,), big.antonyms)
        for index in range(3):
            self.assertEqual((small.constituents[index],), big.constituents[index].antonyms)

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
        self.assertEqual("A1", concept.constituents[0].level)
        self.assertEqual("A2", concept.constituents[1].level)

    def test_missing_level(self):
        """Test that the concept has no level if the concept dict does not contain one."""
        concept = self.create_concept("one", dict(level=dict(none="EP"), fi="Yksi", nl="Eén"))
        self.assertEqual(None, concept.level)

    def test_meaning_only_label(self):
        """Test that a label between brackets is used as meaning but not as label."""
        concept = self.create_concept("mämmi", dict(fi="Mämmi", nl="(Finse paascake)"))
        self.assertEqual(("Mämmi",), concept.labels("fi"))
        self.assertEqual((), concept.labels("nl"))
        self.assertEqual((("Finse paascake",)), concept.meanings("nl"))
