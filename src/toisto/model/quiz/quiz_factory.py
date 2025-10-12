"""Quiz factory."""

from dataclasses import dataclass

from ..language import LanguagePair
from ..language.concept import Concept
from .quiz import Quiz, Quizzes
from .quiz_type import NON_GRAMMATICAL_QUIZ_TYPES, GrammaticalQuizType, QuizAction, QuizType


@dataclass(frozen=True)
class QuizFactory:
    """Create quizzes for multiple concepts."""

    language_pair: LanguagePair
    actions: tuple[QuizAction, ...]

    def create_quizzes(self, *concepts: Concept) -> Quizzes:
        """Create quizzes for the concepts."""
        return Quizzes(Quizzes().union(*(self.concept_quizzes(concept) for concept in concepts)))

    def concept_quizzes(self, concept: Concept) -> Quizzes:
        """Create the quizzes for a concept."""
        quizzes = Quizzes()
        for quiz_type in (*NON_GRAMMATICAL_QUIZ_TYPES, GrammaticalQuizType()):
            quizzes = quizzes | self._quizzes(concept, quiz_type)
        return quizzes

    def _quizzes(
        self,
        concept: Concept,
        quiz_type: QuizType,
    ) -> Quizzes:
        """Create the quizzes with the given quiz type for a concept."""
        return Quizzes(
            Quiz(self.language_pair, concept, question, answers, quiz_type, action)
            for question, answers, action in quiz_type.questions_and_answers(self.language_pair, concept)
            if not self.actions or action in self.actions
        )


def create_quizzes(language_pair: LanguagePair, quiz_types: tuple[QuizType, ...], *concepts: Concept) -> Quizzes:
    """Create quizzes for the concepts, using the target and source language."""
    actions = tuple(quiz_type.action for quiz_type in quiz_types)
    return QuizFactory(language_pair, actions).create_quizzes(*concepts)
