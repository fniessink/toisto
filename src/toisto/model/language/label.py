"""Labels."""

from __future__ import annotations

import re
from collections.abc import Sequence
from functools import cached_property
from typing import ClassVar, Final

from . import Language

SpellingAlternatives = dict[Language, dict[re.Pattern[str], str]]

END_OF_SENTENCE_PUNCTUATION = "?!."


class Label:
    """Class representing labels for concepts."""

    __slots__ = ("__dict__", "language", "_value")  # Without adding __dict__ to slots @cached_property does not work

    # Labels can have one question note and multiple answer notes. The question note is shown before a quiz is
    # presented to the user. The answer notes are shown afterwards. The format is:
    # 'label;question note;answer note 1;answer note 2;...'
    # If the label itself ends with an asterisk it's a colloquial label, i.e. spoken language only.
    NOTE_SEP: Final = ";"
    COLLOQUIAL_POSTFIX: Final = "*"
    QUESTION_NOTE_INDEX: Final = 1
    ANSWER_NOTE_INDEX: Final = 2
    SPELLING_ALTERNATIVES_SEP: Final = "|"
    ALTERNATIVES_TO_GENERATE: ClassVar[SpellingAlternatives] = {}  # These are loaded upon start of the application

    def __init__(self, language: Language, value: str) -> None:
        """Initialize the label."""
        self.language = language
        self._value = value

    def __eq__(self, other: object) -> bool:
        """Return whether the labels are equal."""
        if isinstance(other, Label):
            return self.language == other.language and self.without_notes == other.without_notes
        return False

    def __ne__(self, other: object) -> bool:
        """Return whether the labels are not equal."""
        if isinstance(other, Label):
            return self.language != other.language or self.without_notes != other.without_notes
        return True

    def __bool__(self) -> bool:
        """Return whether the label is empty or not."""
        return bool(self._value)

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(f"{self.language}{self}")

    def __str__(self) -> str:
        """Return the label string value."""
        return self._value

    @property
    def non_generated_spelling_alternatives(self) -> Labels:
        """Extract the spelling alternatives from the label."""
        return label_factory(self.language, self.without_notes.split(self.SPELLING_ALTERNATIVES_SEP))

    @cached_property
    def spelling_alternatives(self) -> Labels:
        """Extract the spelling alternatives from the label and generate additional spelling alternatives."""
        alternatives = self.non_generated_spelling_alternatives
        generated_alternatives = set()
        for alternative in alternatives:
            for pattern, replacement in self.ALTERNATIVES_TO_GENERATE.get(self.language, {}).items():
                if re.search(pattern, str(alternative)):
                    generated_alternative = Label(self.language, re.sub(pattern, replacement, str(alternative)))
                    if alternative.starts_with_upper_case:
                        generated_alternative = generated_alternative.with_upper_case_first_letter
                    generated_alternatives.add(generated_alternative)
        return alternatives + tuple(generated_alternatives)

    @property
    def question_note(self) -> str:
        """Return the label question note."""
        has_question_note = self._value.count(self.NOTE_SEP) >= self.QUESTION_NOTE_INDEX
        return self._value.split(self.NOTE_SEP)[self.QUESTION_NOTE_INDEX] if has_question_note else ""

    @property
    def answer_notes(self) -> Sequence[str]:
        """Return the label answer notes."""
        has_answer_notes = self._value.count(self.NOTE_SEP) >= self.ANSWER_NOTE_INDEX
        return self._value.split(self.NOTE_SEP)[self.ANSWER_NOTE_INDEX :] if has_answer_notes else ()

    @property
    def without_notes(self) -> str:
        """Return the label without the notes."""
        return self._value.split(self.NOTE_SEP)[0]

    @property
    def with_lower_case_first_letter(self) -> Label:
        """Return the label with the first letter lower cased."""
        return Label(self.language, self._value[0].lower() + self._value[1:])

    @property
    def with_upper_case_first_letter(self) -> Label:
        """Return the label with the first letter upper cased."""
        return Label(self.language, self._value[0].upper() + self._value[1:])

    @property
    def lower_case(self) -> Label:
        """Return the label in lower case."""
        return Label(self.language, self._value.lower())

    @property
    def is_colloquial(self) -> bool:
        """Return whether this is a colloquial label."""
        return self.without_notes.endswith(self.COLLOQUIAL_POSTFIX)

    @property
    def is_complete_sentence(self) -> bool:
        """Return whether this is a complete sentence (starts with an upper case letter and ends with punctuation)."""
        return self.starts_with_upper_case and self.ends_with_punctuation

    @property
    def starts_with_upper_case(self) -> bool:
        """Return whether the label starts with an upper case letter."""
        return self._value[0].isupper()

    @property
    def has_upper_case(self) -> bool:
        """Return whether the label has one or more upper case letters."""
        return any(char.isupper() for char in self._value)

    @property
    def ends_with_punctuation(self) -> bool:
        """Return whether the label ends with punctuation."""
        return self.without_notes.strip(self.COLLOQUIAL_POSTFIX)[-1] in END_OF_SENTENCE_PUNCTUATION

    @property
    def pronounceable(self) -> str:
        """Return the label as text that can be sent to a speech synthesizer."""
        return self.without_notes.rstrip(self.COLLOQUIAL_POSTFIX).replace("'", "").replace("-", " ")


Labels = tuple[Label, ...]


def label_factory(language: Language, string: str | list[str]) -> Labels:
    """Instantiate the labels from a string or list of strings."""
    labels = string if isinstance(string, list) else [string]
    return tuple(Label(language, label) for label in labels if not label.startswith("("))


def meaning_factory(language: Language, string: str | list[str]) -> Labels:
    """Instantiate the meanings from a string or list of strings."""
    meanings = string if isinstance(string, list) else [string]
    return tuple(
        Label(language, meaning.removeprefix("(").removesuffix(")"))
        for meaning in meanings
        if not meaning.endswith(Label.COLLOQUIAL_POSTFIX)
    )
