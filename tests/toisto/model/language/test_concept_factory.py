"""Concept factory unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.language.concept import Concept
from toisto.model.language.label import Label

from ....base import LabelDict, ToistoTestCase


class ConcepFactoryTest(ToistoTestCase):
    """Unit tests for the concept factory class."""

    def setUp(self) -> None:
        """Extend to set up test fixtures."""
        super().setUp()
        Concept.instances.clear()

    def test_leaf_concept(self):
        """Test that a leaf concept has no constituent concepts."""
        concept = self.create_concept(
            "english",
            labels=[{"label": "English", "language": EN}, {"label": "Engels", "language": NL}],
        )
        self.assertEqual((), concept.constituents)

    def test_leaf_concept_with_note(self):
        """Test that a leaf concept can have a note."""
        notes = ["In English, the names of languages are capitalized"]
        concept = self.create_concept("english", labels=[{"label": "English", "language": EN, "note": notes}])
        self.assertEqual(tuple(notes), concept.labels(EN)[0].answer_notes)

    def test_leaf_concept_with_tip(self):
        """Test that a leaf concept can have a tip."""
        tip = "A tip"
        concept = self.create_concept("english", labels=[{"label": "English", "language": EN, "tip": tip}])
        self.assertEqual(tip, concept.labels(EN)[0].question_note)

    def test_leaf_concept_with_colloquial_label(self):
        """Test that a leaf concept can have a colloquial label."""
        concept = self.create_concept("thanks", labels=[{"label": "kiiti", "language": FI, "colloquial": True}])
        self.assertTrue(concept.labels(FI)[0].colloquial)

    def test_composite_concept(self):
        """Test that a composite concept has constituent concepts."""
        concept = self.create_concept(
            "morning",
            labels=[
                {"label": {"singular": "aamu", "plural": "aamut"}, "language": FI},
                {"label": {"singular": "de ochtend", "plural": "de ochtenden"}, "language": NL},
            ],
        )
        self.assertEqual(2, len(concept.constituents))

    def test_composite_concept_with_colloquial_labels(self):
        """Test that a composite concept has constituent concepts."""
        concept = self.create_concept(
            "tram",
            labels=[{"label": {"singular": "ratikka", "plural": "ratikat"}, "language": FI, "colloquial": True}],
        )
        for constituent in concept.constituents:
            self.assertTrue(constituent.labels(FI)[0].colloquial)

    def test_composite_concept_with_one_colloquial_label(self):
        """Test that a composite concept has constituent concepts."""
        concept = self.create_concept(
            "three",
            labels=[
                {"label": {"cardinal": "kolme", "ordinal": "kolmes"}, "language": FI},
                {"label": "kol", "language": FI, "colloquial": True},
            ],
        )
        self.assertEqual((Label(FI, "kol", colloquial=True),), concept.labels(FI))
        self.assertEqual((Label(FI, "kolme"), Label(FI, "kolmes")), concept.constituents.labels(FI))

    def test_roots(self):
        """Test that a concept can have roots."""
        concept = self.create_concept(
            "mall",
            {"roots": ["shop", "centre"]},
            labels=[{"label": "kauppakeskus", "language": FI}, {"label": "het winkelcentrum", "language": NL}],
        )
        shop = self.create_concept("shop", labels=[{"label": "kauppa", "language": FI}])
        centre = self.create_concept("centre", labels=[{"label": "keskusta", "language": FI}])
        self.assertEqual((shop, centre), concept.roots(FI))
        self.assertEqual((concept,), shop.compounds(FI))

    def test_language_specific_roots(self):
        """Test that a concept can have a root in one language but not in another."""
        decade = self.create_concept(
            "decade",
            {"roots": {"fi": "year"}},
            labels=[{"label": "vuosikymmen", "language": FI}, {"label": "decade", "language": EN}],
        )
        year = self.create_concept("year", labels=[{"label": "vuosi", "language": FI}])
        self.assertEqual((year,), decade.roots(FI))
        self.assertEqual((), decade.roots(EN))

    def test_roots_are_recursive(self):
        """Test that the roots of a concept are recursive."""
        diner_table_chair = self.create_concept(
            "diner table chair",
            {"roots": ["diner table", "chair"]},
            labels=[{"label": "diner table chair", "language": EN}, {"label": "de eettafelstoel", "language": NL}],
        )
        diner_table = self.create_concept(
            "diner table",
            {"roots": "table"},
            labels=[{"label": "diner table", "language": EN}, {"label": "de eettafel", "language": NL}],
        )
        chair = self.create_concept(
            "chair", labels=[{"label": "chair", "language": EN}, {"label": "de stoel", "language": NL}]
        )
        table = self.create_concept(
            "table", labels=[{"label": "table", "language": EN}, {"label": "de tafel", "language": NL}]
        )
        self.assertEqual((diner_table, chair, table), diner_table_chair.roots(EN))

    def test_homograph(self):
        """Test that a concept can have a homograph concept."""
        wind_label: LabelDict = {"concept": ["wind (weather)", "wind (verb)"], "label": "wind", "language": EN}
        wind_weather = self.create_concept("wind (weather)", labels=[wind_label])
        wind_verb = self.create_concept("wind (verb)", labels=[wind_label])
        self.assertEqual((wind_weather,), wind_verb.get_homographs(Label(EN, "wind")))

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

    def test_antonyms_of_composite(self):
        """Test that a composite concept can have an antonym."""
        big = self.create_concept(
            "big",
            {"antonym": "small"},
            labels=[
                {
                    "label": {
                        "positive degree": "big",
                        "comparative degree": "bigger",
                        "superlative degree": "biggest",
                    },
                    "language": EN,
                },
            ],
        )
        small = self.create_concept(
            "small",
            labels=[
                {
                    "label": {
                        "positive degree": "small",
                        "comparative degree": "smaller",
                        "superlative degree": "smallest",
                    },
                    "language": EN,
                },
            ],
        )
        self.assertEqual((small,), big.get_related_concepts("antonym"))
        for index in range(3):
            self.assertEqual((small.constituents[index],), big.constituents[index].get_related_concepts("antonym"))

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

    def test_answer_of_composite(self):
        """Test that a composite concept can have answers."""
        question = self.create_concept(
            "question",
            {"answer": "answer"},
            labels=[{"label": {"singular": "Puhutko englantia?", "plural": "Puhutteko englantia?"}, "language": FI}],
        )
        answer = self.create_concept(
            "answer",
            labels=[{"label": {"singular": "Puhun.", "plural": "Puhumme."}, "language": FI}],
        )
        self.assertEqual((answer,), question.get_related_concepts("answer"))
        for index in range(2):
            self.assertEqual((answer.constituents[index],), question.constituents[index].get_related_concepts("answer"))

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
