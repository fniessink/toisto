"""Unit tests for quiz relations that the quiz factory creates."""

from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import GrammaticalQuizType, ListenOnlyQuizType, TranslationQuizType

from ....base import EN_NL, FI_NL
from .test_quiz_factory import QuizFactoryTestCase


class QuizRelationsTest(QuizFactoryTestCase):
    """Unit tests for the quiz relations that the quiz factory creates."""

    def test_translation_quizzes_block_listening_quizzes(self):
        """Test that translation quizzes block listening quizzes."""
        quizzes = create_quizzes(FI_NL, self.create_noun())
        translation_quizzes = quizzes.by_quiz_type(TranslationQuizType)
        listening_quizzes = quizzes.by_quiz_type(ListenOnlyQuizType)
        for quiz in listening_quizzes:
            self.assertTrue(quiz.is_blocked_by(Quizzes(translation_quizzes)))

    def test_non_grammatical_quizzes_block_grammatical_quizzes(self):
        """Test that listening and translation quizzes block grammatical quizzes."""
        quizzes = create_quizzes(FI_NL, self.create_noun_with_grammatical_number())
        grammatical_quizzes = quizzes.by_quiz_type(GrammaticalQuizType)
        non_grammatical_quizzes = quizzes - grammatical_quizzes
        for quiz in grammatical_quizzes:
            self.assertTrue(quiz.is_blocked_by(Quizzes(non_grammatical_quizzes)))

    def test_earlier_grammatical_quizzes_block_later_grammatical_quizzes(self):
        """Test that e.g. quizzes for singular forms block quizzes for plural forms."""
        quizzes = create_quizzes(FI_NL, self.create_noun_with_grammatical_number())
        singular_quizzes = {quiz for quiz in quizzes if "singular" in quiz.concept.concept_id}
        plural_quizzes = {quiz for quiz in quizzes if "plural" in quiz.concept.concept_id}
        for quiz in plural_quizzes:
            self.assertTrue(quiz.is_blocked_by(Quizzes(singular_quizzes)))

    def test_constituent_concept_quizzes_block_composite_concept_quizzes(self):
        """Test that quizzes for constituent quizzes block quizzes for their composite concepts."""
        quizzes = create_quizzes(FI_NL, self.create_noun_with_grammatical_number())
        composite_quizzes = {quiz for quiz in quizzes if "/" not in quiz.concept.concept_id}
        constituent_quizzes = {quiz for quiz in quizzes if "/" in quiz.concept.concept_id}
        for quiz in composite_quizzes:
            self.assertTrue(quiz.is_blocked_by(Quizzes(constituent_quizzes)))

    def test_nested_constituent_concept_quizzes_block_composite_concept_quizzes(self):
        """Test that nested quizzes for constituent quizzes block quizzes for their composite concepts."""
        quizzes = create_quizzes(EN_NL, self.create_noun_with_grammatical_number_and_gender())
        feminine_quizzes = {quiz for quiz in quizzes if "feminine" in quiz.concept.concept_id}
        masculine_quizzes = {quiz for quiz in quizzes if "cat/plural/masculine" in quiz.concept.concept_id}
        for quiz in masculine_quizzes:
            self.assertTrue(quiz.is_blocked_by(Quizzes(feminine_quizzes)))
