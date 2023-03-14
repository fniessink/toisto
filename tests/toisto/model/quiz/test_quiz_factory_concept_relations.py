"""Concept relations unit tests."""

from toisto.model.quiz.quiz_factory import QuizFactory

from .test_quiz_factory import QuizFactoryTestCase


class ConceptRootsTest(QuizFactoryTestCase):
    """Unit tests for roots."""

    def test_concept_relationship_leaf_concept(self):
        """Test that leaf concepts can declare to have roots."""
        mall = self.create_concept("mall", dict(roots=["shop", "centre"], fi="kauppakeskus", nl="het winkelcentrum"))
        shop = self.create_concept("shop", dict(fi="kauppa"))
        centre = self.create_concept("centre", dict(fi="keskusta"))
        self.assertEqual(
            (shop, centre),
            self.create_quizzes(mall, "fi", "nl").pop().concept.roots("fi"),
        )

    def test_concept_relationship_composite_concept(self):
        """Test that composite concepts can declare to have roots."""
        mall = self.create_concept(
            "mall",
            dict(
                roots=["shop", "centre"],
                singular=dict(fi="kauppakeskus", nl="het winkelcentrum"),
                plural=dict(fi="kauppakeskukset", nl="de winkelcentra"),
            ),
        )
        shop = self.create_concept("shop", dict(fi="kauppa"))
        centre = self.create_concept("centre", dict(fi="keskusta"))
        for quiz in self.create_quizzes(mall, "fi", "nl"):
            self.assertIn(shop, quiz.concept.roots("fi"))
            self.assertIn(centre, quiz.concept.roots("fi"))

    def test_concept_relationship_leaf_concept_one_root(self):
        """Test that leaf concepts can declare to have one root."""
        capital = self.create_concept("capital", dict(roots="city", fi="pääkaupunki", en="capital"))
        city = self.create_concept("city", dict(fi="kaupunki"))
        self.assertEqual((city,), self.create_quizzes(capital, "fi", "en").pop().concept.roots("fi"))

    def test_generated_concept_ids_for_constituent_concepts(self):
        """Test that constituent concepts get a generated concept id."""
        concept = self.create_noun_with_grammatical_number()
        expected_concept_ids = {
            self.create_quiz(concept, "fi", "nl", "aamu", ["de ochtend"], "read"): "morning/singular",
            self.create_quiz(concept, "fi", "fi", "aamu", ["aamu"], "listen"): "morning/singular",
            self.create_quiz(concept, "nl", "fi", "de ochtend", ["aamu"], "write"): "morning/singular",
            self.create_quiz(concept, "fi", "nl", "aamut", ["de ochtenden"], "read"): "morning/plural",
            self.create_quiz(concept, "fi", "fi", "aamut", ["aamut"], "listen"): "morning/plural",
            self.create_quiz(concept, "nl", "fi", "de ochtenden", ["aamut"], "write"): "morning/plural",
            self.create_quiz(concept, "fi", "fi", "aamu", ["aamut"], "pluralize"): "morning",
            self.create_quiz(concept, "fi", "fi", "aamut", ["aamu"], "singularize"): "morning",
        }
        for quiz in self.create_quizzes(concept, "fi", "nl"):
            self.assertEqual(expected_concept_ids[quiz], quiz.concept.concept_id)


class AntonymConceptsTest(QuizFactoryTestCase):
    """Unit tests for antonym concepts."""

    def test_antonym_leaf_concepts(self):
        """Test that quizzes are generated for concepts with antonym concepts."""
        big = self.create_concept("big", dict(antonym="small", en="big"))
        small = self.create_concept("small", dict(antonym="big", en="small"))
        quizzes = QuizFactory("en", "en").create_quizzes(big, small)
        for concept, question, answer in [(big, "big", "small"), (small, "small", "big")]:
            antonym = self.create_quiz(concept, "en", "en", question, [answer], "antonym")
            self.assertIn(antonym, quizzes)

    def test_antonym_quiz_order(self):
        """Test that before quizzing for an antonym, the anytonym itself has been quizzed."""
        big = self.create_concept("big", dict(antonym="small", en="big"))
        small = self.create_concept("small", dict(antonym="big", en="small"))
        quizzes = QuizFactory("en", "en").create_quizzes(big, small)
        antonym_quizzes = {quiz for quiz in quizzes if "antonym" in quiz.quiz_types}
        other_quizzes = quizzes - antonym_quizzes
        for antonym_quiz in antonym_quizzes:
            for other_quiz in other_quizzes:
                message = f"{antonym_quiz.key} should be blocked by {other_quiz.key}, but isn't"
                self.assertTrue(antonym_quiz.is_blocked_by({other_quiz}), message)
