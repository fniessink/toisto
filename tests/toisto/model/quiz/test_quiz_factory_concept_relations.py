"""Concept relations unit tests."""

from toisto.model.quiz.quiz_factory import QuizFactory

from .test_quiz_factory import QuizFactoryTestCase


class ConceptUsesRelationshipsTest(QuizFactoryTestCase):
    """Unit tests for uses relationships between concepts."""

    def test_concept_relationship_leaf_concept(self):
        """Test that concepts can declare to use, i.e. depend on, other concepts."""
        concept = self.create_concept("mall", dict(uses=["shop", "centre"], fi="Kauppakeskus", nl="Het winkelcentrum"))
        self.assertEqual(("shop", "centre"), self.create_quizzes(concept, "fi", "nl").pop().used_concepts)

    def test_concept_relationship_composite_concept(self):
        """Test that concepts can declare to use, i.e. depend on, other concepts."""
        concept = self.create_concept(
            "mall",
            dict(
                uses=["shop", "centre"],
                singular=dict(fi="Kauppakeskus", nl="Het winkelcentrum"),
                plural=dict(fi="Kauppakeskukset", nl="De winkelcentra"),
            ),
        )
        for quiz in self.create_quizzes(concept, "fi", "nl"):
            self.assertIn("shop", quiz.used_concepts)
            self.assertIn("centre", quiz.used_concepts)

    def test_concept_relationship_leaf_concept_one_uses(self):
        """Test that concepts can declare to use, i.e. depend on, other concepts."""
        concept = self.create_concept("capital", dict(uses="city", fi="Pääkaupunki", en="Capital"))
        self.assertEqual(("city",), self.create_quizzes(concept, "fi", "en").pop().used_concepts)

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
            self.assertEqual(expected_concept_ids[quiz], quiz.concept_id)


class OppositeConceptsTest(QuizFactoryTestCase):
    """Unit tests for opposite concepts."""

    def test_opposite_leaf_concepts(self):
        """Test that quizzes are generated for concepts with opposite other concepts."""
        big = self.create_concept("big", dict(opposite="small", en="Big"))
        small = self.create_concept("small", dict(opposite="big", en="Small"))
        quizzes = QuizFactory("en", "en").create_quizzes(big, small)
        for question, answer in [("Big", "Small"), ("Small", "Big")]:
            opposite = self.create_quiz(big, "en", "en", question, [answer], "opposite")
            self.assertIn(opposite, quizzes)
