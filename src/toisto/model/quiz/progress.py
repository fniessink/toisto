"""Progress model class."""

from collections import deque

from toisto.model.language import Language
from toisto.model.language.concept import Concept

from .quiz import Quiz, Quizzes
from .retention import Retention

ProgressDict = dict[str, dict[str, str | int]]


class Progress:
    """Keep track of progress on quizzes."""

    def __init__(self, progress_dict: ProgressDict, target_language: Language, skip_concepts: int = 5) -> None:
        self.__progress_dict = {key: Retention.from_dict(value) for key, value in progress_dict.items()}
        self.target_language = target_language
        self.__recent_concepts: deque[Concept] = deque(maxlen=skip_concepts)

    def mark_correct_answer(self, quiz: Quiz) -> None:
        """Increase the retention of the quiz."""
        self.__progress_dict.setdefault(quiz.key, Retention()).increase()

    def mark_incorrect_answer(self, quiz: Quiz) -> None:
        """Reset the retention of the quiz."""
        self.__progress_dict.setdefault(quiz.key, Retention()).reset()

    def next_quiz(self, quizzes: Quizzes) -> Quiz | None:
        """Return the next quiz."""
        eligible_quizzes = Quizzes(quiz for quiz in quizzes if self.__is_eligible(quiz))
        quizzes_for_concepts_in_progress = Quizzes(
            quiz for quiz in eligible_quizzes if self.__has_concept_in_progress(quiz, quizzes)
        )
        quizzes_in_progress = Quizzes(quiz for quiz in quizzes_for_concepts_in_progress if self.__in_progress(quiz))
        for potential_quizzes in [quizzes_in_progress, quizzes_for_concepts_in_progress, eligible_quizzes]:
            unblocked_quizzes = self.__unblocked_quizzes(potential_quizzes, eligible_quizzes, quizzes)
            if quiz := unblocked_quizzes.lowest_level():
                self.__recent_concepts.append(quiz.concept.base_concept)
                return quiz
        return None

    def get_retention(self, quiz: Quiz) -> Retention:
        """Return the quiz retention."""
        return self.__progress_dict.get(quiz.key, Retention())

    def __is_eligible(self, quiz: Quiz) -> bool:
        """Return whether the quiz is not silenced and not the current quiz."""
        return quiz.concept.base_concept not in self.__recent_concepts and not self.get_retention(quiz).is_silenced()

    def __has_concept_in_progress(self, quiz: Quiz, quizzes: Quizzes) -> bool:
        """Return whether the quiz's concept has been presented to the user before."""
        quizzes_for_same_concept = quizzes.by_concept(quiz.concept)
        return any(self.__in_progress(quiz_for_same_concept) for quiz_for_same_concept in quizzes_for_same_concept)

    def __in_progress(self, quiz: Quiz) -> bool:
        """Return whether the quiz has been presented to the user before."""
        return quiz.key in self.__progress_dict

    def __unblocked_quizzes(self, potential_quizzes: Quizzes, eligible_quizzes: Quizzes, quizzes: Quizzes) -> Quizzes:
        """Return the quizzes that are not blocked by other quizzes.

        Quiz A is blocked by quiz B if the concept of quiz A is a compound with a root that is quizzed by quiz B.
        """
        return Quizzes(
            quiz
            for quiz in potential_quizzes
            if not self.__root_concepts_have_quizzes(quiz, eligible_quizzes, quizzes)
            and not quiz.is_blocked_by(eligible_quizzes)
        )

    def __root_concepts_have_quizzes(self, quiz: Quiz, eligible_quizzes: Quizzes, quizzes: Quizzes) -> bool:
        """Return whether the quiz's concept has root concepts that have quizzes."""
        target_language = quiz.answer_language if "write" in quiz.quiz_types else quiz.question_language
        return any(
            other_quiz
            for root in quiz.concept.related_concepts.roots(target_language)
            for other_quiz in quizzes.by_concept(root)
            if other_quiz != quiz and other_quiz in eligible_quizzes
        )

    def as_dict(self) -> dict[str, dict[str, int | str]]:
        """Return the progress as dict."""
        return {key: value.as_dict() for key, value in self.__progress_dict.items()}
