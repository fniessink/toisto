"""Concept factory unit tests."""

from toisto.model.language.concept_factory import create_concept
from toisto.model.language.label import Label

from ....base import ToistoTestCase


class ConcepFactoryTest(ToistoTestCase):
    """Unit tests for the concept factory class."""

    def test_leaf_concept(self):
        """Test that a leaf concept has no constituent concepts."""
        concept = create_concept("english", dict(en=["English"], nl=["Engels"]))
        self.assertEqual((), concept.constituents)

    def test_composite_concept(self):
        """Test that a composite concept has constituent concepts."""
        concept = create_concept(
            "morning",
            dict(singular=dict(fi="aamu", nl="de ochtend"), plural=dict(fi="aamut", nl="de ochtenden")),
        )
        self.assertEqual(2, len(concept.constituents))

    def test_roots(self):
        """Test that a concept can have roots."""
        concept = create_concept("mall", dict(roots=["shop", "centre"], fi="kauppakeskus", nl="het winkelcentrum"))
        shop = create_concept("shop", dict(fi="kauppa"))
        centre = create_concept("centre", dict(fi="keskusta"))
        self.assertEqual((shop, centre), concept.roots("fi"))

    def test_language_specific_roots(self):
        """Test that a concept can have a root in one language but not in another."""
        decade = create_concept("decade", dict(roots=dict(fi="year"), fi="vuosikymmen", en="decade"))
        year = create_concept("year", dict(fi="vuosi"))
        self.assertEqual((year,), decade.roots("fi"))
        self.assertEqual((), decade.roots("en"))

    def test_antonym(self):
        """Test that a concept can have an antonym concept."""
        big = create_concept("big", dict(antonym="small", en="big"))
        small = create_concept("small", dict(en="small"))
        self.assertEqual((small,), big.antonyms)

    def test_multiple_antonyms(self):
        """Test that a concept can have multiple antonyms."""
        big = create_concept("big", dict(antonym=["small", "little"], en="big"))
        little = create_concept("little", dict(en="little"))
        small = create_concept("small", dict(en="small"))
        self.assertEqual((small, little), big.antonyms)

    def test_antonyms_of_composite(self):
        """Test that a composite concept can have an antonym."""
        big = create_concept(
            "big",
            {
                "antonym": "small",
                "positive degree": dict(en="big"),
                "comparative degree": dict(en="bigger"),
                "superlative degree": dict(en="biggest"),
            },
        )
        small = create_concept(
            "small",
            {
                "positive degree": dict(en="small"),
                "comparative degree": dict(en="smaller"),
                "superlative degree": dict(en="smallest"),
            },
        )
        self.assertEqual((small,), big.antonyms)
        for index in range(3):
            self.assertEqual((small.constituents[index],), big.constituents[index].antonyms)

    def test_answer(self):
        """Test that a concept can have an answer relation with another concept."""
        question = create_concept("ice cream", dict(en=["Do you like ice cream?"], answer="yes"))
        answer = create_concept("yes", dict(en="Yes!"))
        self.assertEqual((answer,), question.answers)

    def test_multiple_answers(self):
        """Test that a concept can have an answer relation with multiple concepts."""
        question = create_concept("ice cream", dict(en=["Do you like ice cream?"], answer=["yes", "no"]))
        yes = create_concept("yes", dict(en="Yes!"))
        no = create_concept("no", dict(en="No!"))
        self.assertEqual((yes, no), question.answers)

    def test_answer_of_composite(self):
        """Test that a composite concept can have answers."""
        question = create_concept(
            "question",
            {
                "answer": "answer",
                "singular": dict(fi="Puhutko englantia?"),
                "plural": dict(fi="Puhutteko englantia?"),
            },
        )
        answer = create_concept(
            "answer",
            {
                "singular": dict(fi="Puhun."),
                "plural": dict(fi="Puhumme."),
            },
        )
        self.assertEqual((answer,), question.answers)
        for index in range(2):
            self.assertEqual((answer.constituents[index],), question.constituents[index].answers)

    def test_meaning_only_label(self):
        """Test that a label between brackets is used as meaning but not as label."""
        concept = create_concept("Finnish Eastern cake", dict(fi="mämmi", nl="(Finse paascake)"))
        self.assertEqual((Label("fi", "mämmi"),), concept.labels("fi"))
        self.assertEqual((), concept.labels("nl"))
        self.assertEqual((Label("nl", "Finse paascake"),), concept.meanings("nl"))

    def test_answer_only(self):
        """Test that a concept can be flagged as answer only."""
        concept = create_concept("yes", {"answer-only": True, "en": "Yes, I do.", "fi": "Pidän."})
        self.assertTrue(concept.answer_only)
