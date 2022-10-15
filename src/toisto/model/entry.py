"""Entry classes."""

from dataclasses import dataclass
from typing import cast, Literal

from ..metadata import Language
from .quiz import Quiz


EntryDict = dict[Language, str | list[str]]
NounType = Literal["plural", "singular"]
NounEntryDict = dict[NounType, EntryDict]


@dataclass
class Entry:
    """Class representing a word or phrase from a deck."""

    question_language: Language
    answer_language: Language
    questions: list[str]
    answers: list[str]

    def quizzes(self, language: Language) -> list[Quiz]:  # pylint: disable=unused-argument
        """Generate the possible quizzes from the entry."""
        question_language, answer_language = self.question_language, self.answer_language
        questions, answers = self.questions, self.answers
        return (
            [Quiz(question_language, answer_language, question, answers) for question in questions] +
            [Quiz(answer_language, question_language, answer, questions) for answer in answers]
        )

    @classmethod
    def from_dict(cls, entry_dict: EntryDict) -> "Entry":
        """Instantiate an entry from a dict."""
        question_language, answer_language = list(entry_dict.keys())
        question = entry_dict[question_language]
        questions = question if isinstance(question, list) else [question]
        answer = entry_dict[answer_language]
        answers = answer if isinstance(answer, list) else [answer]
        return cls(question_language, answer_language, questions, answers)


@dataclass
class NounEntry:
    """A noun with singular and plural versions."""

    singular: Entry
    plural: Entry

    def quizzes(self, language: Language) -> list[Quiz]:
        """Generate the possible quizzes from the entry."""
        if language == self.singular.question_language:
            pluralize = [
                Quiz(language, language, question, self.plural.questions, "pluralize")
                for question in self.singular.questions
            ]
            singularize = [
                Quiz(language, language, question, self.singular.questions, "singularize")
                for question in self.plural.questions
            ]
        else:
            pluralize = [
                Quiz(language, language, answer, self.plural.answers, "pluralize")
                for answer in self.singular.answers
            ]
            singularize = [
                Quiz(language, language, answer, self.singular.answers, "singularize")
                for answer in self.plural.answers
            ]
        return self.singular.quizzes(language) + self.plural.quizzes(language) + pluralize + singularize

    @classmethod
    def from_dict(cls, entry_dict: NounEntryDict) -> "NounEntry":
        """Instantiate an entry from a dict."""
        singular_entry = Entry.from_dict(entry_dict["singular"])
        plural_entry = Entry.from_dict(entry_dict["plural"])
        return cls(singular_entry, plural_entry)


def entry_factory(entry_dict: EntryDict | NounEntryDict) -> Entry | NounEntry:
    """Create an entry from the entry dict."""
    if "singular" in entry_dict and "plural" in entry_dict:
        return NounEntry.from_dict(cast(NounEntryDict, entry_dict))
    return Entry.from_dict(cast(EntryDict, entry_dict))
