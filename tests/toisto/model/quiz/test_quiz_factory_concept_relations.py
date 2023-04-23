"""Concept relations unit tests."""

from toisto.model.language.concept_factory import create_concept
from toisto.model.quiz.quiz_factory import create_quizzes

from .test_quiz_factory import QuizFactoryTestCase


class ConceptRootsTest(QuizFactoryTestCase):
    """Unit tests for roots."""

    def test_concept_relationship_leaf_concept(self):
        """Test that leaf concepts can declare to have roots."""
        mall = create_concept("mall", dict(roots=["shop", "centre"], fi="kauppakeskus", nl="het winkelcentrum"))
        shop = create_concept("shop", dict(fi="kauppa"))
        centre = create_concept("centre", dict(fi="keskusta"))
        self.assertEqual(
            (shop, centre),
            create_quizzes("fi", "nl", mall).pop().concept.roots("fi"),
        )

    def test_concept_relationship_composite_concept(self):
        """Test that composite concepts can declare to have roots."""
        mall = create_concept(
            "mall",
            dict(
                roots=["shop", "centre"],
                singular=dict(fi="kauppakeskus", nl="het winkelcentrum"),
                plural=dict(fi="kauppakeskukset", nl="de winkelcentra"),
            ),
        )
        shop = create_concept("shop", dict(fi="kauppa"))
        centre = create_concept("centre", dict(fi="keskusta"))
        for quiz in create_quizzes("fi", "nl", mall):
            self.assertIn(shop, quiz.concept.roots("fi"))
            self.assertIn(centre, quiz.concept.roots("fi"))

    def test_concept_relationship_leaf_concept_one_root(self):
        """Test that leaf concepts can declare to have one root."""
        capital = create_concept("capital", dict(roots="city", fi="pääkaupunki", en="capital"))
        city = create_concept("city", dict(fi="kaupunki"))
        self.assertEqual((city,), create_quizzes("fi", "en", capital).pop().concept.roots("fi"))

    def test_generated_concept_ids_for_constituent_concepts(self):
        """Test that constituent concepts get a generated concept id."""
        concept = self.create_noun_with_grammatical_number()
        expected_concept_ids = {
            ("aamu", "de ochtend"): "morning/singular",
            ("aamu", "aamu"): "morning/singular",
            ("de ochtend", "aamu"): "morning/singular",
            ("aamut", "de ochtenden"): "morning/plural",
            ("aamut", "aamut"): "morning/plural",
            ("de ochtenden", "aamut"): "morning/plural",
            ("aamu", "aamut"): "morning",
            ("aamut", "aamu"): "morning",
        }
        for quiz in create_quizzes("fi", "nl", concept):
            self.assertEqual(expected_concept_ids[(str(quiz.question), str(quiz.answers[0]))], quiz.concept.concept_id)


class AntonymConceptsTest(QuizFactoryTestCase):
    """Unit tests for antonym concepts."""

    def test_antonym_leaf_concepts(self):
        """Test that quizzes are generated for concepts with antonym concepts."""
        big = create_concept("big", dict(antonym="small", en="big"))
        small = create_concept("small", dict(antonym="big", en="small"))
        quizzes = create_quizzes("en", "en", big, small)
        for concept, question, answer in [(big, "big", "small"), (small, "small", "big")]:
            antonym = self.create_quiz(concept, "en", "en", question, [answer], "antonym")
            self.assertIn(antonym, quizzes)

    def test_antonym_quiz_order(self):
        """Test that before quizzing for an antonym, the anytonym itself has been quizzed."""
        big = create_concept("big", dict(antonym="small", en="big"))
        small = create_concept("small", dict(antonym="big", en="small"))
        quizzes = create_quizzes("en", "en", big, small)
        antonym_quizzes = {quiz for quiz in quizzes if "antonym" in quiz.quiz_types}
        other_quizzes = quizzes - antonym_quizzes
        for antonym_quiz in antonym_quizzes:
            for other_quiz in other_quizzes:
                message = f"{antonym_quiz.key} should be blocked by {other_quiz.key}, but isn't"
                self.assertTrue(antonym_quiz.is_blocked_by({other_quiz}), message)


class AnswerConceptsTest(QuizFactoryTestCase):
    """Unit tests for answer concepts."""

    def test_answer_leaf_concepts(self):
        """Test that quizzes are generated for concepts with answer concepts."""
        question = create_concept("question", dict(answer="answer", en="How are you?"))
        answer = create_concept("answer", dict(en="I'm fine, thank you."))
        quizzes = create_quizzes("en", "en", question, answer)
        answer_quiz = self.create_quiz(question, "en", "en", "How are you?", ["I'm fine, thank you."], "answer")
        self.assertIn(answer_quiz, quizzes)

    def test_answer_composite_concepts(self):
        """Test that quizzes are generated for composite concepts with answer concepts."""
        question = create_concept(
            "question",
            dict(answer="answer", singular=dict(en="How are you?;singular"), plural=dict(en="How are you?;plural")),
        )
        answer = create_concept(
            "answer",
            dict(singular=dict(en="I'm fine, thank you."), plural=dict(en="We're fine, thank you.")),
        )
        quizzes = create_quizzes("en", "en", question, answer)
        singular_answer_quiz = self.create_quiz(
            question,
            "en",
            "en",
            "How are you?;singular",
            ["I'm fine, thank you."],
            "answer",
        )
        plural_answer_quiz = self.create_quiz(
            question,
            "en",
            "en",
            "How are you?;plural",
            ["We're fine, thank you."],
            "answer",
        )
        self.assertIn(singular_answer_quiz, quizzes)
        self.assertIn(plural_answer_quiz, quizzes)

    def test_multiple_answers(self):
        """Test that quizzes can have multiple answers."""
        question = create_concept("question", dict(answer=["fine", "good"], en="How are you?"))
        fine = create_concept("fine", dict(en="I'm fine, thank you."))
        good = create_concept("good", dict(en="I'm doing good, thank you."))
        quiz = [quiz for quiz in create_quizzes("en", "en", question, fine, good) if "answer" in quiz.quiz_types][0]
        self.assertEqual((fine.labels("en")[0], good.labels("en")[0]), quiz.answers)

    def test_answer_quiz_order(self):
        """Test that before quizzing for an answer to a question, the answer itself has been quizzed."""
        question = create_concept("question", dict(answer="answer", en="How are you?"))
        answer = create_concept("answer", dict(en="I'm fine, thank you."))
        quizzes = create_quizzes("en", "en", question, answer)
        answer_quizzes = {quiz for quiz in quizzes if "answer" in quiz.quiz_types}
        other_quizzes = quizzes - answer_quizzes
        for answer_quiz in answer_quizzes:
            for other_quiz in other_quizzes:
                message = f"{answer_quiz.key} should be blocked by {other_quiz.key}, but isn't"
                self.assertTrue(answer_quiz.is_blocked_by({other_quiz}), message)
