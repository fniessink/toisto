"""Progress model class."""

import random

from .quiz import Quiz
from .quiz_progress import QuizProgress


class Progress:
    """Keep track of progress on quizzes."""
    def __init__(self, progress_dict: dict[str, dict[str, int | str]]) -> None:
        self.progress_dict = {key: QuizProgress.from_dict(value) for key, value in progress_dict.items()}
        self.current_quiz: Quiz | None = None

    def update(self, quiz: Quiz, correct: bool) -> None:
        """Update the progress on the quiz."""
        key = str(quiz)
        self.progress_dict.setdefault(key, QuizProgress()).update(correct)

    def get_progress(self, quiz: Quiz) -> QuizProgress:
        """Return the progress on the quiz."""
        key = str(quiz)
        return self.progress_dict.get(key, QuizProgress())

    def next_quiz(self, quizzes: list[Quiz]) -> Quiz | None:
        """Return the next quiz."""
        if eligible_quizzes := [quiz for quiz in quizzes if self.is_eligible(quiz)]:
            if len(eligible_quizzes) > 1 and self.current_quiz in eligible_quizzes:
                eligible_quizzes.remove(self.current_quiz)
            self.current_quiz = random.choice(eligible_quizzes)
            return self.current_quiz
        return None
#
    def is_eligible(self, quiz: Quiz) -> bool:
        """Is the quiz eligible?"""
        return not self.get_progress(quiz).is_silenced()

    def as_dict(self) -> dict[str, dict[str, int | str]]:
        """Return the progress as dict."""
        return {key: value.as_dict() for key, value in self.progress_dict.items()}
