"""Concept factory unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.language.concept import Concept
from toisto.model.language.label import Label

from ....base import ToistoTestCase


class ConcepFactoryTest(ToistoTestCase):
    """Unit tests for the concept factory class."""

    def setUp(self) -> None:
        """Extend to set up test fixtures."""
        super().setUp()
        Concept.instances.clear()

    def test_concept_with_composite_labels(self):
        """Test a concept with composite labels."""
        concept = self.create_concept(
            "morning",
            labels=[
                {"label": {"singular": "aamu", "plural": "aamut"}, "language": FI},
                {"label": {"singular": "de ochtend", "plural": "de ochtenden"}, "language": NL},
            ],
        )
        aamu = Label(FI, "aamu", grammatical_categories=("singular",))
        aamut = Label(FI, "aamut", grammatical_categories=("plural",))
        self.assertEqual((aamu, aamut), concept.labels(FI))
        ochtend = Label(NL, "de ochtend", grammatical_categories=("singular",))
        ochtenden = Label(NL, "de ochtenden", grammatical_categories=("plural",))
        self.assertEqual((ochtend, ochtenden), concept.labels(NL))

    def test_concept_with_colloquial_labels(self):
        """Test a concept with colloquial labels."""
        concept = self.create_concept(
            "tram",
            labels=[{"label": {"singular": "ratikka", "plural": "ratikat"}, "language": FI, "colloquial": True}],
        )
        for label in concept.labels(FI):
            self.assertTrue(label.colloquial)

    def test_concept_with_colloquial_and_non_colloquial_labels(self):
        """Test a concept with colloquial and non-colloquial labels."""
        concept = self.create_concept(
            "three",
            labels=[
                {"label": {"cardinal": "kolme", "ordinal": "kolmes"}, "language": FI},
                {"label": "kol", "language": FI, "colloquial": True},
            ],
        )
        kolme = Label(FI, "kolme", grammatical_categories=("cardinal",))
        kolmes = Label(FI, "kolmes", grammatical_categories=("ordinal",))
        kol = Label(FI, "kol", colloquial=True)
        self.assertEqual((kolme, kolmes, kol), concept.labels(FI))

    def test_label_roots(self):
        """Test that a concept can have a label with roots."""
        kitchen = self.create_concept("kitchen", labels=[{"label": "de keuken", "language": NL}])
        table = self.create_concept("table", labels=[{"label": "de tafel", "language": NL}])
        kitchen_table = self.create_concept(
            "kitchen table",
            labels=[{"label": "de keukentafel", "language": NL, "roots": ["de keuken", "de tafel"]}],
        )
        (keuken,) = kitchen.labels(NL)
        (tafel,) = table.labels(NL)
        self.assertEqual((keuken, tafel), kitchen_table.labels(NL)[0].roots)

    def test_composite_label_roots(self):
        """Test that a concept can have composite labels with roots."""
        kitchen = self.create_concept("kitchen", labels=[{"label": "de keuken", "language": NL}])
        table = self.create_concept("table", labels=[{"label": "de tafel", "language": NL}])
        kitchen_table = self.create_concept(
            "kitchen table",
            labels=[
                {
                    "label": {"singular": "de keukentafel", "plural": "de keukentafels"},
                    "language": NL,
                    "roots": ["de keuken", "de tafel"],
                }
            ],
        )
        (keuken,) = kitchen.labels(NL)
        (tafel,) = table.labels(NL)
        for label in kitchen_table.labels(NL):
            self.assertEqual((keuken, tafel), label.roots)

    def test_antonym(self):
        """Test that a concept can have an antonym concept."""
        big = self.create_concept("big", {"antonym": "small"}, labels=[{"label": "big", "language": EN}])
        small = self.create_concept("small", labels=[{"label": "small", "language": EN}])
        self.assertEqual((small,), big.get_related_concepts("antonym"))

    def test_multiple_antonyms(self):
        """Test that a concept can have multiple antonyms."""
        big = self.create_concept("big", {"antonym": ["small", "little"]}, labels=[{"label": "big", "language": EN}])
        little = self.create_concept("little", labels=[{"label": "little", "language": EN}])
        small = self.create_concept("small", labels=[{"label": "small", "language": EN}])
        self.assertEqual((small, little), big.get_related_concepts("antonym"))

    def test_hypernym_and_hyponym(self):
        """Test that a concept can have a hypernym concept, and that the hypernym has the concept as hyponym."""
        canine = self.create_concept("canine", labels=[{"label": "canine", "language": EN}])
        dog = self.create_concept("dog", {"hypernym": "canine"}, labels=[{"label": "dog", "language": EN}])
        self.assertEqual((canine,), dog.get_related_concepts("hypernym"))
        self.assertEqual((dog,), canine.get_related_concepts("hyponym"))

    def test_hypernyms_and_hyponyms_are_transitive(self):
        """Test that a concept's hypernyms and hyponyms are transitive."""
        animal = self.create_concept("animal", labels=[{"label": "animal", "language": EN}])
        canine = self.create_concept("canine", {"hypernym": "animal"}, labels=[{"label": "canine", "language": EN}])
        dog = self.create_concept("dog", {"hypernym": "canine"}, labels=[{"label": "dog", "language": EN}])
        self.assertEqual((canine, animal), dog.get_related_concepts("hypernym"))
        self.assertEqual((canine, dog), animal.get_related_concepts("hyponym"))

    def test_holonym_and_meronym(self):
        """Test that a concept can have a holonym concept, and that the meronym has the concept as holonym."""
        animal = self.create_concept("animal", labels=[{"label": "animal", "language": EN}])
        tail = self.create_concept("tail", {"holonym": "animal"}, labels=[{"label": "tail", "language": EN}])
        self.assertEqual((animal,), tail.get_related_concepts("holonym"))
        self.assertEqual((tail,), animal.get_related_concepts("meronym"))

    def test_holonyms_and_meronyms_are_transitive(self):
        """Test that a concept's holonyms and meronyms are transitive."""
        animal = self.create_concept("animal", labels=[{"label": "animal", "language": EN}])
        head = self.create_concept("head", {"holonym": "animal"}, labels=[{"label": "head", "language": EN}])
        eye = self.create_concept("eye", {"holonym": "head"}, labels=[{"label": "eye", "language": EN}])
        self.assertEqual((head, animal), eye.get_related_concepts("holonym"))
        self.assertEqual((head, eye), animal.get_related_concepts("meronym"))

    def test_answer(self):
        """Test that a concept can have an answer relation with another concept."""
        question = self.create_concept(
            "ice cream", {"answer": "yes"}, labels=[{"label": "Do you like ice cream?", "language": EN}]
        )
        answer = self.create_concept("yes", labels=[{"label": "Yes!", "language": EN}])
        self.assertEqual((answer,), question.get_related_concepts("answer"))

    def test_multiple_answers(self):
        """Test that a concept can have an answer relation with multiple concepts."""
        question = self.create_concept(
            "ice cream", {"answer": ["yes", "no"]}, labels=[{"label": "Do you like ice cream?", "language": EN}]
        )
        yes = self.create_concept("yes", labels=[{"label": "Yes!", "language": EN}])
        no = self.create_concept("no", labels=[{"label": "No!", "language": EN}])
        self.assertEqual((yes, no), question.get_related_concepts("answer"))

    def test_example(self):
        """Test that a concept can have an example."""
        concept = self.create_concept(
            "next to", {"example": "the museum is next to the church"}, labels=[{"label": "vieressä", "language": FI}]
        )
        example = self.create_concept(
            "the museum is next to the church", labels=[{"label": "Museo on kirkon vieressä.", "language": FI}]
        )
        self.assertEqual((example,), concept.get_related_concepts("example"))

    def test_multiple_examples(self):
        """Test that a concept can have multiple examples."""
        examples = ["the car is black", "the cars are black"]
        concept = self.create_concept("black", {"example": examples}, labels=[{"label": "musta", "language": FI}])
        example1 = self.create_concept("the car is black", labels=[{"label": "Auto on musta.", "language": FI}])
        example2 = self.create_concept("the cars are black", labels=[{"label": "Autot ovat mustia.", "language": FI}])
        self.assertEqual((example1, example2), concept.get_related_concepts("example"))

    def test_meaning_only_label(self):
        """Test that a label between brackets is used as meaning but not as label."""
        concept = self.create_concept(
            "Finnish Eastern cake",
            labels=[
                {"label": "mämmi", "language": FI},
                {"label": "Finse paascake", "language": NL, "meaning-only": True},
            ],
        )
        self.assertEqual((Label(FI, "mämmi"),), concept.labels(FI))
        self.assertEqual((), concept.labels(NL))
        self.assertEqual((Label(NL, "Finse paascake"),), concept.meanings(NL))

    def test_answer_only(self):
        """Test that a concept can be flagged as answer only."""
        concept = self.create_concept(
            "yes",
            {"answer-only": True},
            labels=[{"label": "Yes, I do.", "language": EN}, {"label": "Pidän.", "language": FI}],
        )
        self.assertTrue(concept.answer_only)

    def test_multiple_labels_in_the_same_language(self):
        """Test that a concept can have multiple labels in the same language."""
        concept = self.create_concept(
            "yes",
            labels=[
                {"label": "yes", "language": EN},
                {"label": "kyllä", "language": FI},
                {"label": "joo", "language": FI},
            ],
        )
        self.assertEqual((Label(FI, "kyllä"), (Label(FI, "joo"))), concept.labels(FI))
        self.assertEqual((Label(EN, "yes"),), concept.meanings(EN))
        self.assertEqual((), concept.labels(NL))
