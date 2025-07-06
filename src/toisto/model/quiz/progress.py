"""Progress model class."""

from collections import deque

from toisto.model.language import Language
from toisto.model.language.concept import Concept
from toisto.persistence.progress_format import ProgressDict

from .evaluation import Evaluation
from .quiz import Quiz, Quizzes
from .quiz_type import QuizType
from .retention import Retention


class Progress:
    """Keep track of progress on quizzes."""

    def __init__(
        self,
        target_language: Language,
        quizzes: Quizzes,
        progress_dict: ProgressDict,
        skip_concepts: int = 5,
    ) -> None:
        self.__progress_dict = {
            key: Retention.from_dict(value) for key, value in progress_dict.items() if self.valid(key)
        }
        self.target_language = target_language
        self.quizzes = quizzes
        self.__recent_concepts: deque[Concept] = deque(maxlen=skip_concepts)
        self.answers = dict.fromkeys(Evaluation, 0)

    def valid(self, key: str) -> bool:
        """Return whether the key is valid."""
        quiz_type = key.rsplit(":", maxsplit=1)[-1]
        return bool(QuizType.actions.get_values(quiz_type))

    def mark_evaluation(self, quiz: Quiz, evaluation: Evaluation) -> None:
        """Mark the evaluation.

        If the answer was correct, increase the retention of the quiz, and pause related quizzes for a little while.
        If the answer was incorrect or skipped, reset the retention of the quiz.
        """
        self.answers[evaluation] += 1
        match evaluation:
            case Evaluation.CORRECT:
                self.__progress_dict.setdefault(quiz.key, Retention()).increase()
                self.__pause_related_quizzes(quiz)
            case Evaluation.INCORRECT | Evaluation.SKIPPED:
                self.__progress_dict.setdefault(quiz.key, Retention()).reset()
            case _:
                return

    def __pause_related_quizzes(self, quiz: Quiz) -> None:
        """Pause related quizzes for a little while."""
        for related_quiz in self.quizzes.related_quizzes(quiz):
            if related_quiz == quiz:
                continue
            self.__progress_dict.setdefault(related_quiz.key, Retention()).pause()

    def next_quiz(self) -> Quiz | None:
        """Return the next quiz."""
        eligible_quizzes = self.eligible_quizzes()
        quizzes_for_concepts_in_progress = Quizzes(
            quiz for quiz in eligible_quizzes if self.__has_concept_in_progress(quiz)
        )
        quizzes_in_progress = Quizzes(quiz for quiz in quizzes_for_concepts_in_progress if self.__in_progress(quiz))
        for potential_quizzes in [quizzes_in_progress, quizzes_for_concepts_in_progress, eligible_quizzes]:
            if unblocked_quizzes := self.__unblocked_quizzes(potential_quizzes, eligible_quizzes):
                quiz = unblocked_quizzes.pop()
                self.__recent_concepts.append(quiz.concept.base_concept)
                return quiz
        return None

    def get_retention(self, quiz: Quiz) -> Retention:
        """Return the quiz retention."""
        return self.__progress_dict.get(quiz.key, Retention())

    def eligible_quizzes(self) -> Quizzes:
        """Return the eligible quizzes."""
        return Quizzes(quiz for quiz in self.quizzes if self.__is_eligible(quiz))

    def __is_eligible(self, quiz: Quiz) -> bool:
        """Return whether the quiz is not silenced and not the current quiz."""
        return quiz.concept.base_concept not in self.__recent_concepts and not self.get_retention(quiz).is_silenced()

    def __has_concept_in_progress(self, quiz: Quiz) -> bool:
        """Return whether the quiz's concept has been presented to the user before."""
        quizzes_for_same_concept = self.quizzes.by_concept(quiz.concept)
        return any(self.__in_progress(quiz_for_same_concept) for quiz_for_same_concept in quizzes_for_same_concept)

    def __in_progress(self, quiz: Quiz) -> bool:
        """Return whether the quiz has been presented to the user before."""
        return quiz.key in self.__progress_dict

    def __unblocked_quizzes(self, potential_quizzes: Quizzes, eligible_quizzes: Quizzes) -> Quizzes:
        """Return the quizzes that are not blocked by other quizzes.

        Quiz A is blocked by quiz B if the concept of quiz A is a compound with a root that is quizzed by quiz B.
        """
        return Quizzes(
            quiz
            for quiz in potential_quizzes
            if not self.__root_labels_have_quizzes(quiz, eligible_quizzes) and not quiz.is_blocked_by(eligible_quizzes)
        )

    def __root_labels_have_quizzes(self, quiz: Quiz, eligible_quizzes: Quizzes) -> bool:
        """Return whether the quiz's labels have root labels that have quizzes."""
        for label in {quiz.question, *quiz.answers}:
            for root in label.roots:
                for other_quiz in self.quizzes.by_label(root):
                    if other_quiz != quiz and other_quiz in eligible_quizzes:
                        return True
        return False

    def as_dict(self) -> ProgressDict:
        """Return the progress as dict."""
        return {key: value.as_dict() for key, value in self.__progress_dict.items()}
