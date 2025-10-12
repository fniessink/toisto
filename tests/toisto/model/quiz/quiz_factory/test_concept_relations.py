"""Concept relations unit tests."""

from toisto.model.language import EN
from toisto.model.language.concept import Concept, ConceptId
from toisto.model.language.label import Label
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import ANSWER, ANTONYM
from toisto.tools import first

from .....base import EN_NL, LabelDict
from .quiz_factory_test_case import QuizFactoryTestCase


class AntonymQuizzesTest(QuizFactoryTestCase):
    """Unit tests for antonym quizzes."""

    def create_antonyms(self, *, add_comparative_degree: bool = False) -> tuple[Concept, Concept]:
        """Create two antonym concepts."""
        small_label: LabelDict = {"label": "small", "language": EN}
        if add_comparative_degree:
            small_label["label"] = {"positive degree": "small", "comparative degree": "smaller"}
        small = self.create_concept("small", {"antonym": ConceptId("big")}, labels=[small_label])
        big = self.create_concept("big", {"antonym": ConceptId("small")}, labels=[{"label": "big", "language": EN}])
        return small, big

    def test_antonym_concepts(self):
        """Test that quizzes are generated for concepts with antonym concepts."""
        small, big = self.create_antonyms()
        quizzes = create_quizzes(EN_NL, (), big, small)
        for concept, answer in [(big, "small"), (small, "big")]:
            antonym = self.create_quiz(EN_NL, concept, concept.labels(EN)[0], [Label(EN, answer)], ANTONYM)
            self.assertIn(antonym, quizzes)

    def test_antonym_concepts_with_different_grammatical_forms(self):
        """Test that quizzes are generated for concepts with antonym concepts that have grammar."""
        small, big = self.create_antonyms(add_comparative_degree=True)
        quizzes = create_quizzes(EN_NL, (), big, small)
        for concept, answer in [(big, "small"), (small, "big")]:
            antonym = self.create_quiz(EN_NL, concept, concept.labels(EN)[0], [Label(EN, answer)], ANTONYM)
            self.assertIn(antonym, quizzes)

    def test_antonym_quiz_order(self):
        """Test that before quizzing for an antonym, the anytonym itself has been quizzed."""
        small, big = self.create_antonyms()
        quizzes = create_quizzes(EN_NL, (), big, small)
        antonym_quizzes = Quizzes(quiz for quiz in quizzes if quiz.has_quiz_type(ANTONYM))
        other_quizzes = quizzes - antonym_quizzes
        for antonym_quiz in antonym_quizzes:
            for other_quiz in other_quizzes:
                message = f"{antonym_quiz.key} should be blocked by {other_quiz.key}, but isn't"
                self.assertTrue(antonym_quiz.is_blocked_by(Quizzes({other_quiz})), message)


class AnswerQuizzesTest(QuizFactoryTestCase):
    """Unit tests for answer concepts."""

    def test_single_answer(self):
        """Test that quizzes are generated for concepts with an answer concept."""
        question = self.create_concept(
            "question", {"answer": ConceptId("answer")}, labels=[{"label": "How are you?", "language": EN}]
        )
        answer = self.create_concept("answer", labels=[{"label": "I'm fine, thank you.", "language": EN}])
        quizzes = create_quizzes(EN_NL, (), question, answer)
        (answer_label,) = answer.labels(EN)
        answer_quiz = self.create_quiz(EN_NL, question, question.labels(EN)[0], [answer_label], ANSWER)
        self.assertIn(answer_quiz, quizzes)

    def test_answer_grammatical_categories(self):
        """Test that quizzes are generated for multiple grammatical categories."""
        question = self.create_concept(
            "question",
            {"answer": ConceptId("answer")},
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
        singular_answer_quiz = self.create_quiz(EN_NL, question, how_are_you, [i_am_fine], ANSWER)
        plural_answer_quiz = self.create_quiz(EN_NL, question, how_are_you_all, [we_are_fine], ANSWER)
        self.assertIn(singular_answer_quiz, quizzes)
        self.assertIn(plural_answer_quiz, quizzes)

    def test_multiple_answers(self):
        """Test that quizzes can have multiple answers."""
        question = self.create_concept(
            "question",
            {"answer": [ConceptId("fine"), ConceptId("good")]},
            labels=[{"label": "How are you?", "language": EN}],
        )
        fine = self.create_concept("fine", labels=[{"label": "I'm fine, thank you.", "language": EN}])
        good = self.create_concept("good", labels=[{"label": "I'm doing good, thank you.", "language": EN}])
        quiz = first(create_quizzes(EN_NL, (ANSWER,), question, fine, good))
        self.assertEqual((fine.labels(EN)[0], good.labels(EN)[0]), quiz.answers)

    def test_answer_quiz_order(self):
        """Test that before quizzing for an answer to a question, the answer itself has been quizzed."""
        question = self.create_concept(
            "question", {"answer": ConceptId("answer")}, labels=[{"label": "How are you?", "language": EN}]
        )
        answer = self.create_concept("answer", labels=[{"label": "I'm fine, thank you.", "language": EN}])
        quizzes = create_quizzes(EN_NL, (), question, answer)
        answer_quizzes = Quizzes(quiz for quiz in quizzes if quiz.has_quiz_type(ANSWER))
        other_quizzes = quizzes - answer_quizzes
        for answer_quiz in answer_quizzes:
            for other_quiz in other_quizzes:
                message = f"{answer_quiz.key} should be blocked by {other_quiz.key}, but isn't"
                self.assertTrue(answer_quiz.is_blocked_by(Quizzes({other_quiz})), message)
