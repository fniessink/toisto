"""Model classes."""

from dataclasses import dataclass
from datetime import datetime, timedelta
import math
import random

from .match import match


@dataclass
class Quiz:
    """Class representing one question word or phrase question with one ore more correct answers."""
    question_language: str
    answer_language: str
    question: str
    answers: list[str]

    def is_correct(self, guess: str) -> bool:
        """Return whether the guess is correct."""
        return match(guess, *self.answers)

    def get_answer(self) -> str:
        """Return the first answer."""
        return self.answers[0]


@dataclass
class Entry:
    """Class representing a word or phrase from a deck."""
    question_language: str
    answer_language: str
    questions: list[str]
    answers: list[str]

    def quizzes(self) -> list[Quiz]:
        """Generate the possible quizzes from the entry."""
        return (
            [Quiz(self.question_language, self.answer_language, question, self.answers) for question in self.questions]
            +
            [Quiz(self.answer_language, self.question_language, answer, self.questions) for answer in self.answers]
        )

    @classmethod
    def from_dict(cls, entry_dict: dict[str, str | list[str]]) -> "Entry":
        """Instantiate an entry from a dict."""
        question_language, answer_language = list(entry_dict.keys())
        question = entry_dict[question_language]
        questions = question if isinstance(question, list) else [question]
        answer = entry_dict[answer_language]
        answers = answer if isinstance(answer, list) else [answer]
        return cls(question_language, answer_language, questions, answers)


@dataclass
class QuizProgress:
    """Class to keep track of progress on one quiz."""

    count: int = 0  # The number of consecutive correct guesses
    silence_until: datetime | None = None  # Don't quiz this again until after the datetime

    def update(self, correct: bool) -> None:
        """Update the progress of the quiz."""
        if correct:
            self.count += 1
        else:
            self.count = 0
        self.silence_until = self.__calculate_next_quiz() if self.count > 1 else None

    def is_silenced(self):
        """Return whether the quiz is silenced."""
        return self.silence_until > datetime.now() if self.silence_until else False

    def __calculate_next_quiz(self) -> datetime:
        """Calculate when to quiz again based on the number of correct guesses."""
        # Graph of function below: https://www.desmos.com/calculator/itvdhmh6ex
        max_timedelta = timedelta(days=90)  # How often do we quiz when user has perfect recall?
        slope = 0.25  # How fast do we get to the max timedelta?
        x_shift = -5.6  # Determines the minimum period at count = 2
        y_shift = 1  # Make zero the minimum y value instead of -1
        time_delta = (math.tanh(slope * self.count + x_shift) + y_shift) * (max_timedelta / 2)
        return datetime.now() + time_delta

    def as_dict(self) -> dict[str, int | str]:
        """Return the quiz progress as dict."""
        result: dict[str, int | str] = dict(count=self.count)
        if self.silence_until:
            result["silence_until"] = self.silence_until.isoformat()
        return result

    @classmethod
    def from_dict(cls, quiz_progress_dict: dict[str, int | str]) -> "QuizProgress":
        """Instantiate a quiz progress from a dict."""
        count = int(quiz_progress_dict.get("count", 0))
        silence_until_text = str(quiz_progress_dict.get("silence_until", ""))
        silence_until = datetime.fromisoformat(silence_until_text) if silence_until_text else None
        return cls(count, silence_until)


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
        eligible_quizzes = [quiz for quiz in quizzes if not self.get_progress(quiz).is_silenced()]
        if not eligible_quizzes:
            return None
        min_progress = min(self.get_progress(quiz).count for quiz in eligible_quizzes)
        next_quizzes = [quiz for quiz in eligible_quizzes if self.get_progress(quiz).count == min_progress]
        return random.choice(next_quizzes)

    def as_dict(self) -> dict[str, dict[str, int | str]]:
        """Return the progress as dict."""
        return {key: value.as_dict() for key, value in self.progress_dict.items()}
