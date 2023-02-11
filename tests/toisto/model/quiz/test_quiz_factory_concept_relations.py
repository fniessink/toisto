"""Concept relations unit tests."""

from toisto.model.quiz.quiz_factory import QuizFactory

from .test_quiz_factory import QuizFactoryTestCase


class ConceptRootsTest(QuizFactoryTestCase):
    """Unit tests for roots."""

    def test_concept_relationship_leaf_concept(self):
        """Test that leaf concepts can declare to have roots."""
        mall = self.create_concept("mall", dict(roots=["shop", "centre"], fi="Kauppakeskus", nl="Het winkelcentrum"))
        shop = self.create_concept("shop", dict(fi="Kauppa"))
        centre = self.create_concept("centre", dict(fi="Keskusta"))
        self.assertEqual((shop, centre), self.create_quizzes(mall, "fi", "nl").pop().concept.root_concepts("fi"))

    def test_concept_relationship_composite_concept(self):
        """Test that composite concepts can declare to have roots."""
        mall = self.create_concept(
            "mall",
            dict(
                roots=["shop", "centre"],
                singular=dict(fi="Kauppakeskus", nl="Het winkelcentrum"),
                plural=dict(fi="Kauppakeskukset", nl="De winkelcentra"),
            ),
        )
        shop = self.create_concept("shop", dict(fi="Kauppa"))
        centre = self.create_concept("centre", dict(fi="Keskusta"))
        for quiz in self.create_quizzes(mall, "fi", "nl"):
            self.assertIn(shop, quiz.concept.root_concepts("fi"))
            self.assertIn(centre, quiz.concept.root_concepts("fi"))

    def test_concept_relationship_leaf_concept_one_root(self):
        """Test that leaf concepts can declare to have one root."""
        capital = self.create_concept("capital", dict(roots="city", fi="Pääkaupunki", en="Capital"))
        city = self.create_concept("city", dict(fi="Kaupunki"))
        self.assertEqual((city,), self.create_quizzes(capital, "fi", "en").pop().concept.root_concepts("fi"))

    def test_generated_concept_ids_for_constituent_concepts(self):
        """Test that constituent concepts get a generated concept id."""
        concept = self.create_noun_with_grammatical_number()
        expected_concept_ids = {
            self.create_quiz(concept, "fi", "nl", "Aamu", ["De ochtend"]): "morning/singular",
            self.create_quiz(concept, "nl", "fi", "De ochtend", ["Aamu"]): "morning/singular",
            self.create_quiz(concept, "fi", "fi", "Aamu", ["Aamu"], "listen"): "morning/singular",
            self.create_quiz(concept, "fi", "nl", "Aamut", ["De ochtenden"]): "morning/plural",
            self.create_quiz(concept, "nl", "fi", "De ochtenden", ["Aamut"]): "morning/plural",
            self.create_quiz(concept, "fi", "fi", "Aamut", ["Aamut"], "listen"): "morning/plural",
            self.create_quiz(concept, "fi", "fi", "Aamu", ["Aamut"], "pluralize"): "morning",
            self.create_quiz(concept, "fi", "fi", "Aamut", ["Aamu"], "singularize"): "morning",
        }
        for quiz in self.create_quizzes(concept, "fi", "nl"):
            self.assertEqual(expected_concept_ids[quiz], quiz.concept.concept_id)


class AntonymConceptsTest(QuizFactoryTestCase):
    """Unit tests for antonym concepts."""

    def test_antonym_leaf_concepts(self):
        """Test that quizzes are generated for concepts with antonym concepts."""
        big = self.create_concept("big", dict(antonym="small", en="Big"))
        small = self.create_concept("small", dict(antonym="big", en="Small"))
        quizzes = QuizFactory("en", "en").create_quizzes(big, small)
        for question, answer in [("Big", "Small"), ("Small", "Big")]:
            antonym = self.create_quiz(big, "en", "en", question, [answer], "antonym")
            self.assertIn(antonym, quizzes)
