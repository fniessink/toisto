"""Concept relations unit tests."""

from toisto.model.language import EN
from toisto.model.language.label import Label
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import ANSWER, ANTONYM
from toisto.tools import first

from ....base import EN_NL, FI_NL
from .test_quiz_factory import QuizFactoryTestCase


class ConstituentConceptsTest(QuizFactoryTestCase):
    """Unit tests for constituent concepts."""

    def test_generated_concept_ids_for_constituent_concepts(self):
        """Test that constituent concepts get a generated concept id."""
        concept = self.create_noun_with_grammatical_number()
        expected_concept_ids: dict[tuple[str, str], str] = {
            ("aamu", "de ochtend"): "morning/singular",
            ("aamu", "aamu"): "morning/singular",
            ("de ochtend", "aamu"): "morning/singular",
            ("aamut", "de ochtenden"): "morning/plural",
            ("aamut", "aamut"): "morning/plural",
            ("de ochtenden", "aamut"): "morning/plural",
            ("aamu", "aamut"): "morning",
            ("aamut", "aamu"): "morning",
        }
        for quiz in create_quizzes(FI_NL, (), concept):
            self.assertEqual(expected_concept_ids[(str(quiz.question), str(quiz.answers[0]))], quiz.concept.concept_id)


class AntonymConceptsTest(QuizFactoryTestCase):
    """Unit tests for antonym concepts."""

    def setUp(self) -> None:
        """Extend to set up text fixtures."""
        super().setUp()
        self.big = self.create_concept("big", {"antonym": "small"}, labels=[{"label": "big", "language": EN}])
        self.small = self.create_concept("small", {"antonym": "big"}, labels=[{"label": "small", "language": EN}])
        self.quizzes = create_quizzes(EN_NL, (), self.big, self.small)

    def test_antonym_concepts(self):
        """Test that quizzes are generated for concepts with antonym concepts."""
        for concept, answer in [(self.big, "small"), (self.small, "big")]:
            antonym = self.create_quiz(concept, concept.labels(EN)[0], [Label(EN, answer)], ANTONYM)
            self.assertIn(antonym, self.quizzes)

    def test_antonym_quiz_order(self):
        """Test that before quizzing for an antonym, the anytonym itself has been quizzed."""
        antonym_quizzes = Quizzes(quiz for quiz in self.quizzes if quiz.has_quiz_type(ANTONYM))
        other_quizzes = self.quizzes - antonym_quizzes
        for antonym_quiz in antonym_quizzes:
            for other_quiz in other_quizzes:
                message = f"{antonym_quiz.key} should be blocked by {other_quiz.key}, but isn't"
                self.assertTrue(antonym_quiz.is_blocked_by(Quizzes({other_quiz})), message)


class AnswerConceptsTest(QuizFactoryTestCase):
    """Unit tests for answer concepts."""

    def test_single_answer(self):
        """Test that quizzes are generated for concepts with an answer concept."""
        question = self.create_concept(
            "question", {"answer": "answer"}, labels=[{"label": "How are you?", "language": EN}]
        )
        answer = self.create_concept("answer", labels=[{"label": "I'm fine, thank you.", "language": EN}])
        quizzes = create_quizzes(EN_NL, (), question, answer)
        (answer_label,) = answer.labels(EN)
        answer_quiz = self.create_quiz(question, question.labels(EN)[0], [answer_label], ANSWER)
        self.assertIn(answer_quiz, quizzes)

    def test_answer_grammatical_categories(self):
        """Test that quizzes are generated for multiple grammatical categories."""
        question = self.create_concept(
            "question",
            {"answer": "answer"},
            labels=[{"label": {"singular": "How are you?", "plural": "How are you all?"}, "language": EN}],
        )
        answer = self.create_concept(
            "answer",
            labels=[
                {"label": {"singular": "I'm fine, thank you.", "plural": "We're fine, thank you."}, "language": EN}
            ],
        )
        quizzes = create_quizzes(EN_NL, (), question, answer)
        how_are_you, how_are_you_all = question.labels(EN)
        i_am_fine, we_are_fine = answer.labels(EN)
        singular_answer_quiz = self.create_quiz(question, how_are_you, [i_am_fine], ANSWER)
        plural_answer_quiz = self.create_quiz(question, how_are_you_all, [we_are_fine], ANSWER)
        self.assertIn(singular_answer_quiz, quizzes)
        self.assertIn(plural_answer_quiz, quizzes)

    def test_multiple_answers(self):
        """Test that quizzes can have multiple answers."""
        question = self.create_concept(
            "question", {"answer": ["fine", "good"]}, labels=[{"label": "How are you?", "language": EN}]
        )
        fine = self.create_concept("fine", labels=[{"label": "I'm fine, thank you.", "language": EN}])
        good = self.create_concept("good", labels=[{"label": "I'm doing good, thank you.", "language": EN}])
        quiz = first(create_quizzes(EN_NL, (ANSWER,), question, fine, good))
        self.assertEqual((fine.labels(EN)[0], good.labels(EN)[0]), quiz.answers)

    def test_answer_quiz_order(self):
        """Test that before quizzing for an answer to a question, the answer itself has been quizzed."""
        question = self.create_concept(
            "question", {"answer": "answer"}, labels=[{"label": "How are you?", "language": EN}]
        )
        answer = self.create_concept("answer", labels=[{"label": "I'm fine, thank you.", "language": EN}])
        quizzes = create_quizzes(EN_NL, (), question, answer)
        answer_quizzes = Quizzes(quiz for quiz in quizzes if quiz.has_quiz_type(ANSWER))
        other_quizzes = quizzes - answer_quizzes
        for answer_quiz in answer_quizzes:
            for other_quiz in other_quizzes:
                message = f"{answer_quiz.key} should be blocked by {other_quiz.key}, but isn't"
                self.assertTrue(answer_quiz.is_blocked_by(Quizzes({other_quiz})), message)
