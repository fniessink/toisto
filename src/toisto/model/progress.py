"""Progress model class."""

import random

from .quiz import Quiz, Quizzes
from .quiz_progress import QuizProgress


class Progress:
    """Keep track of progress on quizzes."""
    def __init__(self, progress_dict: dict[str, dict[str, int | str]]) -> None:
        self.__progress_dict = {key: QuizProgress.from_dict(value) for key, value in progress_dict.items()}
        self.__current_quiz: Quiz | None = None

    def update(self, quiz: Quiz, correct: bool) -> None:
        """Update the progress on the quiz."""
        self.__progress_dict.setdefault(str(quiz), QuizProgress()).update(correct)

    def get_progress(self, quiz: Quiz) -> QuizProgress:
        """Return the progress on the quiz."""
        return self.__progress_dict.get(str(quiz), QuizProgress())

    def next_quiz(self, quizzes: Quizzes) -> Quiz | None:
        """Return the next quiz."""
        eligible_quizzes = self.__eligible_quizzes(quizzes)
        self.__current_quiz = random.choice(eligible_quizzes) if eligible_quizzes else None
        return self.__current_quiz

    def __eligible_quizzes(self, quizzes: Quizzes) -> Quizzes:
        """Return eligible quizzes."""
        eligible_quizzes = [quiz for quiz in quizzes if not self.__is_silenced(quiz) and quiz != self.__current_quiz]
        quizzes_with_progress = [quiz for quiz in eligible_quizzes if self.__has_progress(quiz)]
        quizzes_without_progress = [quiz for quiz in eligible_quizzes if not self.__has_progress(quiz)]
        return quizzes_without_progress[:3] if len(quizzes_with_progress) < 3 else quizzes_with_progress

    def __is_silenced(self, quiz: Quiz) -> bool:
        """Is the quiz silenced?"""
        return self.get_progress(quiz).is_silenced()

    def __has_progress(self, quiz: Quiz) -> bool:
        """Has the quiz been presented to the user before?"""
        return str(quiz) in self.__progress_dict

    def as_dict(self) -> dict[str, dict[str, int | str]]:
        """Return the progress as dict."""
        return {key: value.as_dict() for key, value in self.__progress_dict.items()}
