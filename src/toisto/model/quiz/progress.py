"""Progress model class."""

import random

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

    def get_retention(self, quiz: Quiz) -> Retention:
        """Return the quiz retention."""
        return self.__progress_dict.get(str(quiz), Retention())

    def next_quiz(self, topics: Topics) -> Quiz | None:
        """Return the next quiz."""
        for must_have_progress in (True, False):
            for topic in topics:
                if quizzes := self.__eligible_quizzes(topic.quizzes, must_have_progress):
                    self.__current_quiz = random.choice(list(quizzes))
                    return self.__current_quiz
        self.__current_quiz = None
        return None

    def __eligible_quizzes(self, quizzes: Quizzes, must_have_progress: bool) -> Quizzes:
        """Return the quizzes that can be the next quiz."""
        eligible = [quiz for quiz in quizzes if not self.__is_silenced(quiz) and quiz != self.__current_quiz]
        eligible_with_progress = [quiz for quiz in eligible if self.__has_progress(quiz)]
        return set(eligible_with_progress if must_have_progress else eligible_with_progress or eligible)

    def __is_silenced(self, quiz: Quiz) -> bool:
        """Is the quiz silenced?"""
        return self.get_retention(quiz).is_silenced()

    def __has_progress(self, quiz: Quiz) -> bool:
        """Has the quiz been presented to the user before?"""
        return str(quiz) in self.__progress_dict

    def as_dict(self) -> dict[str, dict[str, int | str]]:
        """Return the progress as dict."""
        return {key: value.as_dict() for key, value in self.__progress_dict.items()}
