"""Model classes."""

import random

from .quiz import Quiz
from .quiz_progress import QuizProgress


class Progress:
    """Keep track of progress on quizzes."""
    def __init__(self, progress_dict: dict[str, dict[str, int | str]]) -> None:
        self.progress_dict = {key: QuizProgress.from_dict(value) for key, value in progress_dict.items()}

    def update(self, quiz: Quiz, correct: bool) -> None:
        """Update the progress of the quiz."""
        key = str(quiz)
        self.progress_dict.setdefault(key, QuizProgress()).update(correct)

    def get_progress(self, quiz: Quiz) -> QuizProgress:
        """Return the progress of the entry."""
        key = str(quiz)
        return self.progress_dict.get(key, QuizProgress())

    def next_quiz(self, quizzes: list[Quiz]) -> Quiz | None:
        """Return the next quiz."""
        if eligible_quizzes := [quiz for quiz in quizzes if not self.get_progress(quiz).is_silenced()]:
            return random.choice(eligible_quizzes)
        return None

    def as_dict(self) -> dict[str, dict[str, int | str]]:
        """Return the progress as dict."""
        return {key: value.as_dict() for key, value in self.progress_dict.items()}
