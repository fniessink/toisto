"""Progress model class."""

import random

from .quiz import Quiz, Quizzes
from .retention import Retention
from .topic import Topic, Topics


class Progress:
    """Keep track of progress on quizzes."""
    def __init__(self, progress_dict: dict[str, dict[str, str]]) -> None:
        self.__progress_dict = {key: Retention.from_dict(value) for key, value in progress_dict.items()}
        self.__current_quiz: Quiz | None = None
        self.__current_topic: Topic | None = None

    def update(self, quiz: Quiz, correct: bool) -> None:
        """Update the progress on the quiz."""
        self.__progress_dict.setdefault(str(quiz), Retention()).update(correct)

    def get_retention(self, quiz: Quiz) -> Retention:
        """Return the quiz retention."""
        return self.__progress_dict.get(str(quiz), Retention())

    def next_quiz(self, topics: Topics) -> Quiz | None:
        """Return the next quiz."""
        eligible_topics = Topics(set([self.__current_topic])) if self.__current_topic else topics
        self.__current_topic, eligible_quizzes = self.__eligible_quizzes(eligible_topics)
        self.__current_quiz = random.choice(list(eligible_quizzes)) if eligible_quizzes else None
        return self.__current_quiz

    def __eligible_quizzes(self, topics: Topics) -> tuple[Topic | None, Quizzes]:
        """Return eligible quizzes."""
        for topic in topics.topics:
            quizzes = [quiz for quiz in topic.quizzes if not self.__is_silenced(quiz) and quiz != self.__current_quiz]
            if quizzes_with_progress := [quiz for quiz in quizzes if self.__has_progress(quiz)]:
                return topic, set(quizzes_with_progress)
        for topic in topics.topics:
            quizzes = [quiz for quiz in topic.quizzes if not self.__is_silenced(quiz) and quiz != self.__current_quiz]
            if quizzes_without_progress := [quiz for quiz in quizzes if not self.__has_progress(quiz)]:
                return topic, set(quizzes_without_progress)
        return None, set()

    def __is_silenced(self, quiz: Quiz) -> bool:
        """Is the quiz silenced?"""
        return self.get_retention(quiz).is_silenced()

    def __has_progress(self, quiz: Quiz) -> bool:
        """Has the quiz been presented to the user before?"""
        return str(quiz) in self.__progress_dict

    def as_dict(self) -> dict[str, dict[str, str]]:
        """Return the progress as dict."""
        return {key: value.as_dict() for key, value in self.__progress_dict.items()}
