"""Concept factory unit tests."""

from toisto.model.language.label import Label

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
            dict(singular=dict(fi="aamu", nl="de ochtend"), plural=dict(fi="aamut", nl="de ochtenden")),
        )
        self.assertEqual(2, len(concept.constituents))

    def test_roots(self):
        """Test that a concept can have roots."""
        concept = self.create_concept("mall", dict(roots=["shop", "centre"], fi="kauppakeskus", nl="het winkelcentrum"))
        shop = self.create_concept("shop", dict(fi="kauppa"))
        centre = self.create_concept("centre", dict(fi="keskusta"))
        self.assertEqual((shop, centre), concept.roots(self.fi))
        self.assertEqual((concept,), shop.compounds(self.fi))

    def test_language_specific_roots(self):
        """Test that a concept can have a root in one language but not in another."""
        decade = self.create_concept("decade", dict(roots=dict(fi="year"), fi="vuosikymmen", en="decade"))
        year = self.create_concept("year", dict(fi="vuosi"))
        self.assertEqual((year,), decade.roots(self.fi))
        self.assertEqual((), decade.roots(self.en))

    def test_antonym(self):
        """Test that a concept can have an antonym concept."""
        big = self.create_concept("big", dict(antonym="small", en="big"))
        small = self.create_concept("small", dict(en="small"))
        self.assertEqual((small,), big.antonyms)

    def test_multiple_antonyms(self):
        """Test that a concept can have multiple antonyms."""
        big = self.create_concept("big", dict(antonym=["small", "little"], en="big"))
        little = self.create_concept("little", dict(en="little"))
        small = self.create_concept("small", dict(en="small"))
        self.assertEqual((small, little), big.antonyms)

    def test_antonyms_of_composite(self):
        """Test that a composite concept can have an antonym."""
        big = self.create_concept(
            "big",
            {
                "antonym": "small",
                "positive degree": dict(en="big"),
                "comparative degree": dict(en="bigger"),
                "superlative degree": dict(en="biggest"),
            },
        )
        small = self.create_concept(
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

    def test_hypernym_and_hyponym(self):
        """Test that a concept can have a hypernym concept, and that the hypernym has the concept as hyponym."""
        canine = self.create_concept("canine", dict(en="canine"))
        dog = self.create_concept("dog", dict(hypernym="canine", en="dog"))
        self.assertEqual((canine,), dog.hypernyms)
        self.assertEqual((dog,), canine.hyponyms)

    def test_hypernyms_and_hyponyms_are_transitive(self):
        """Test that a concept's hypernyms and hyponyms are transitive."""
        animal = self.create_concept("animal", dict(en="animal"))
        canine = self.create_concept("canine", dict(hypernym="animal", en="canine"))
        dog = self.create_concept("dog", dict(hypernym="canine", en="dog"))
        self.assertEqual((canine, animal), dog.hypernyms)
        self.assertEqual((canine, dog), animal.hyponyms)

    def test_holonym_and_meronym(self):
        """Test that a concept can have a holonym concept, and that the meronym has the concept as holonym."""
        animal = self.create_concept("animal", dict(en="animal"))
        tail = self.create_concept("tail", dict(holonym="animal", en="tail"))
        self.assertEqual((animal,), tail.holonyms)
        self.assertEqual((tail,), animal.meronyms)

    def test_holonyms_and_meronyms_are_transitive(self):
        """Test that a concept's holonyms and meronyms are transitive."""
        animal = self.create_concept("animal", dict(en="animal"))
        head = self.create_concept("head", dict(holonym="animal", en="head"))
        eye = self.create_concept("eye", dict(holonym="head", en="eye"))
        self.assertEqual((head, animal), eye.holonyms)
        self.assertEqual((head, eye), animal.meronyms)

    def test_answer(self):
        """Test that a concept can have an answer relation with another concept."""
        question = self.create_concept("ice cream", dict(en=["Do you like ice cream?"], answer="yes"))
        answer = self.create_concept("yes", dict(en="Yes!"))
        self.assertEqual((answer,), question.answers)

    def test_multiple_answers(self):
        """Test that a concept can have an answer relation with multiple concepts."""
        question = self.create_concept("ice cream", dict(en=["Do you like ice cream?"], answer=["yes", "no"]))
        yes = self.create_concept("yes", dict(en="Yes!"))
        no = self.create_concept("no", dict(en="No!"))
        self.assertEqual((yes, no), question.answers)

    def test_answer_of_composite(self):
        """Test that a composite concept can have answers."""
        question = self.create_concept(
            "question",
            {
                "answer": "answer",
                "singular": dict(fi="Puhutko englantia?"),
                "plural": dict(fi="Puhutteko englantia?"),
            },
        )
        answer = self.create_concept(
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
        concept = self.create_concept("Finnish Eastern cake", dict(fi="mämmi", nl="(Finse paascake)"))
        self.assertEqual((Label(self.fi, "mämmi"),), concept.labels(self.fi))
        self.assertEqual((), concept.labels(self.nl))
        self.assertEqual((Label(self.nl, "Finse paascake"),), concept.meanings(self.nl))

    def test_answer_only(self):
        """Test that a concept can be flagged as answer only."""
        concept = self.create_concept("yes", {"answer-only": True, "en": "Yes, I do.", "fi": "Pidän."})
        self.assertTrue(concept.answer_only)
