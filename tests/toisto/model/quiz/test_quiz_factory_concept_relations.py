"""Concept relations unit tests."""

from .test_quiz_factory import QuizFactoryTestCase


class ConceptRelationshipsTest(QuizFactoryTestCase):
    """Unit tests for relationships between concepts."""

    def test_concept_relationship_leaf_concept(self):
        """Test that concepts can declare to use, i.e. depend on, other concepts."""
        concept = self.create_concept(
            "mall",
            dict(uses=["shop", "centre"], fi="Kauppakeskus", nl="Het winkelcentrum"),
        )
        self.assertEqual(("shop", "centre"), self.create_quizzes(concept, "fi", "nl").pop().uses)

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
            self.assertIn("shop", quiz.uses)
            self.assertIn("centre", quiz.uses)

    def test_concept_relationship_leaf_concept_one_uses(self):
        """Test that concepts can declare to use, i.e. depend on, other concepts."""
        concept = self.create_concept("capital", dict(uses="city", fi="Pääkaupunki", en="Capital"))
        self.assertEqual(("city",), self.create_quizzes(concept, "fi", "en").pop().uses)

    def test_generated_concept_ids_for_constituent_concepts(self):
        """Test that constituent concepts get a generated concept id."""
        concept = self.create_noun_with_grammatical_number()
        expected_concept_ids = {
            self.create_quiz("morning", "fi", "nl", "Aamu", ["De ochtend"]): "morning/singular",
            self.create_quiz("morning", "nl", "fi", "De ochtend", ["Aamu"]): "morning/singular",
            self.create_quiz("morning", "fi", "fi", "Aamu", ["Aamu"], "listen"): "morning/singular",
            self.create_quiz("morning", "fi", "nl", "Aamut", ["De ochtenden"]): "morning/plural",
            self.create_quiz("morning", "nl", "fi", "De ochtenden", ["Aamut"]): "morning/plural",
            self.create_quiz("morning", "fi", "fi", "Aamut", ["Aamut"], "listen"): "morning/plural",
            self.create_quiz("morning", "fi", "fi", "Aamu", ["Aamut"], "pluralize"): "morning",
            self.create_quiz("morning", "fi", "fi", "Aamut", ["Aamu"], "singularize"): "morning",
        }
        for quiz in self.create_quizzes(concept, "fi", "nl"):
            self.assertEqual(expected_concept_ids[quiz], quiz.concept_id)
