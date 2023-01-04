"""Progress model class."""

from ..model_types import equal_or_prefix

from .quiz import Quiz, Quizzes
from .retention import Retention
from .topic import Topics


class Progress:
    """Keep track of progress on quizzes."""
    def __init__(self, progress_dict: dict[str, dict[str, str | int]]) -> None:
        self.__progress_dict = {key: Retention.from_dict(value) for key, value in progress_dict.items()}
        self.__current_quiz: Quiz | None = None

    def update(self, quiz: Quiz, correct: bool) -> None:
        """Update the progress on the quiz."""
        self.__progress_dict.setdefault(str(quiz), Retention()).update(correct)

    def next_quiz(self, topics: Topics) -> Quiz | None:
        """Return the next quiz."""
        all_quizzes = set(quiz for topic in topics for quiz in topic.quizzes if self.__is_eligible(quiz))
        quizzes_with_progress = {quiz for quiz in all_quizzes if self.__has_progress(quiz)}
        quizzes = quizzes_with_progress or all_quizzes
        while quizzes:
            self.__current_quiz = quizzes.pop()
            if not self.__used_concepts_have_quizzes(self.__current_quiz, quizzes):
                return self.__current_quiz
        self.__current_quiz = None
        return None

    def get_retention(self, quiz: Quiz) -> Retention:
        """Return the quiz retention."""
        return self.__progress_dict.get(str(quiz), Retention())

    def __is_eligible(self, quiz: Quiz) -> bool:
        """Return whether the quiz is not silenced and not the current quiz."""
        return quiz != self.__current_quiz and not self.get_retention(quiz).is_silenced()

    def __has_progress(self, quiz: Quiz) -> bool:
        """Has the quiz been presented to the user before?"""
        return str(quiz) in self.__progress_dict

    def __used_concepts_have_quizzes(self, quiz: Quiz, quizzes: Quizzes) -> bool:
        """Return whether the quiz uses concepts that have quizzes."""
        for other_quiz in quizzes:
            for concept_id in quiz.uses:
                if equal_or_prefix(other_quiz.concept_id, concept_id):
                    return True
        return False

    def as_dict(self) -> dict[str, dict[str, int | str]]:
        """Return the progress as dict."""
        return {key: value.as_dict() for key, value in self.__progress_dict.items()}
