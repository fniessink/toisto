"""Progress model class."""

from ..model_types import ConceptId, parent_ids

from .quiz import Quiz, Quizzes
from .retention import Retention
from .topic import Topics


class Progress:
    """Keep track of progress on quizzes."""

    def __init__(self, progress_dict: dict[str, dict[str, str | int]], topics: Topics) -> None:
        self.__progress_dict = {key: Retention.from_dict(value) for key, value in progress_dict.items()}
        self.__topics = topics
        self.__current_quiz: Quiz | None = None
        self.__quizzes_by_concept_id: dict[ConceptId, Quizzes] = {}
        for quiz in self.__topics.quizzes:
            for parent_id in parent_ids(quiz.concept_id):
                self.__quizzes_by_concept_id.setdefault(parent_id, set()).add(quiz)

    def update(self, quiz: Quiz, correct: bool) -> None:
        """Update the progress on the quiz."""
        self.__progress_dict.setdefault(str(quiz), Retention()).update(correct)

    def next_quiz(self) -> Quiz | None:
        """Return the next quiz."""
        eligible_quizzes = {quiz for quiz in self.__topics.quizzes if self.__is_eligible(quiz)}
        quizzes_for_concepts_in_progress = {quiz for quiz in eligible_quizzes if self.__has_concept_in_progress(quiz)}
        quizzes_in_progress = {quiz for quiz in quizzes_for_concepts_in_progress if self.__in_progress(quiz)}
        potential_quizzes = quizzes_in_progress or quizzes_for_concepts_in_progress or eligible_quizzes
        self.__current_quiz = self.__unblocked_quizzes(potential_quizzes).pop() if potential_quizzes else None
        return self.__current_quiz

    def get_retention(self, quiz: Quiz) -> Retention:
        """Return the quiz retention."""
        return self.__progress_dict.get(str(quiz), Retention())

    def __is_eligible(self, quiz: Quiz) -> bool:
        """Return whether the quiz is not silenced and not the current quiz."""
        return quiz != self.__current_quiz and not self.get_retention(quiz).is_silenced()

    def __has_concept_in_progress(self, quiz: Quiz) -> bool:
        """Has the quiz's concept been presented to the user before?"""
        return any(self.__in_progress(other_quiz) for other_quiz in self.__quizzes_by_concept_id[quiz.concept_id])

    def __in_progress(self, quiz: Quiz) -> bool:
        """Has the quiz been presented to the user before?"""
        return str(quiz) in self.__progress_dict

    def __unblocked_quizzes(self, quizzes: Quizzes) -> Quizzes:
        """Return the quizzes that are not blocked by other quizzes.

        Quiz A is blocked by quiz B if the concept of quiz A uses a concept that is quizzed by quiz B.
        """
        return {quiz for quiz in quizzes if not self.__used_concepts_have_quizzes(quiz, quizzes)}

    def __used_concepts_have_quizzes(self, quiz: Quiz, quizzes: Quizzes) -> bool:
        """Return whether the quiz uses concepts that have quizzes."""
        return any(
            other_quiz
            for concept_id in quiz.uses
            for other_quiz in self.__quizzes_by_concept_id[concept_id]
            if other_quiz != quiz and other_quiz in quizzes
        )

    def as_dict(self) -> dict[str, dict[str, int | str]]:
        """Return the progress as dict."""
        return {key: value.as_dict() for key, value in self.__progress_dict.items()}
