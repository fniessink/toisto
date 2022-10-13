"""Entry classes."""

from dataclasses import dataclass

from .quiz import Quiz


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
