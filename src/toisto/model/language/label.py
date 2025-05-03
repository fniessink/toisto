"""Labels."""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Sequence
from functools import cached_property
from itertools import chain
from random import shuffle
from typing import ClassVar, Final

from toisto.tools import first, first_upper

from . import Language

SpellingAlternatives = dict[Language, dict[re.Pattern[str], str]]

END_OF_SENTENCE_PUNCTUATION = "?!."


class Label:
    """Class representing labels for concepts."""

    __slots__ = (
        "__dict__",
        "_colloquial",
        "_notes",
        "_tip",
        "_value",
        "language",
    )  # Without adding __dict__ to slots @cached_property does not work

    # If the label itself ends with an asterisk it's a colloquial label, i.e. spoken language only.
    COLLOQUIAL_POSTFIX: Final = "*"
    SPELLING_ALTERNATIVES_SEP: Final = "|"
    ALTERNATIVES_TO_GENERATE: ClassVar[SpellingAlternatives] = {}  # These are loaded upon start of the application

    def __init__(
        self, language: Language, value: str, notes: tuple[str, ...] = (), tip: str = "", *, colloquial: bool = False
    ) -> None:
        """Initialize the label."""
        self.language = language
        self._colloquial = colloquial
        self._value = value
        self._notes = notes
        self._tip = tip

    def __eq__(self, other: object) -> bool:
        """Return whether the labels are equal."""
        if isinstance(other, Label):
            return self.language == other.language and str(self) == str(other)
        return False

    def __ne__(self, other: object) -> bool:
        """Return whether the labels are not equal."""
        if isinstance(other, Label):
            return self.language != other.language or str(self) != str(other)
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

    __repr__ = __str__

    @property
    def non_generated_spelling_alternatives(self) -> Labels:
        """Extract the spelling alternatives from the label."""
        spelling_alternatives = str(self._value).split(self.SPELLING_ALTERNATIVES_SEP)
        return Labels(
            [
                Label(self.language, spelling_alternative, colloquial=self.is_colloquial)
                for spelling_alternative in spelling_alternatives
            ]
        )

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
        return alternatives + Labels(generated_alternatives)

    @cached_property
    def first_spelling_alternative(self) -> Label:
        """Return the first spelling alternative for the label."""
        return first(self.non_generated_spelling_alternatives)

    @property
    def random_order(self) -> Label:
        """Return the first spelling alternative of the label in random word order."""
        words = str(self.first_spelling_alternative).split(" ")
        shuffle(words)
        return Label(self.language, " ".join(words))

    @property
    def question_note(self) -> str:
        """Return the label question note."""
        return self._tip

    @property
    def answer_notes(self) -> Sequence[str]:
        """Return the label answer notes."""
        return self._notes

    @property
    def with_upper_case_first_letter(self) -> Label:
        """Return the label with the first letter upper cased."""
        return Label(self.language, first_upper(self._value))

    @property
    def lower_case(self) -> Label:
        """Return the label in lower case."""
        return Label(self.language, self._value.lower())

    @property
    def is_colloquial(self) -> bool:
        """Return whether this is a colloquial label."""
        return self._colloquial or (self._value).endswith(self.COLLOQUIAL_POSTFIX)

    @property
    def is_complete_sentence(self) -> bool:
        """Return whether this is a complete sentence (starts with an upper case letter and ends with punctuation)."""
        return self.starts_with_upper_case and self.ends_with_punctuation

    @property
    def starts_with_upper_case(self) -> bool:
        """Return whether the label starts with an upper case letter."""
        return self._value[0].isupper()

    @property
    def ends_with_punctuation(self) -> bool:
        """Return whether the label ends with punctuation."""
        return str(self._value).strip(self.COLLOQUIAL_POSTFIX)[-1] in END_OF_SENTENCE_PUNCTUATION

    @property
    def pronounceable(self) -> str:
        """Return the label as text that can be sent to a speech synthesizer."""
        return str(self._value).rstrip(self.COLLOQUIAL_POSTFIX).replace("'", "").replace("-", " ")

    @property
    def word_count(self) -> int:
        """Return the label word count."""
        return len(str(self.first_spelling_alternative).split(" "))


class Labels:
    """Labels collection."""

    def __init__(self, labels: Iterable[Label] = ()) -> None:
        self._labels = tuple(labels)

    def __repr__(self) -> str:
        """Return the string representation of the labels."""
        return repr(tuple(repr(label) for label in self._labels))

    def __eq__(self, other: object) -> bool:
        """Return whether the labels are equal."""
        if isinstance(other, Labels):
            return self._labels == other._labels
        return self._labels == other

    def __iter__(self) -> Iterator[Label]:
        """Return an iterator over the labels."""
        return iter(self._labels)

    def __add__(self, other: Labels) -> Labels:
        """Return the addition of the labels."""
        return Labels(self._labels + other._labels)

    def __getitem__(self, index: int) -> Label:
        """Return the Label at the specified position."""
        return self._labels[index]

    def __len__(self) -> int:
        """Return the number of labels."""
        return len(self._labels)

    def with_language(self, language: Language) -> Labels:
        """Return the labels with the specified language."""
        return Labels(label for label in self._labels if label.language == language)

    @property
    def non_colloquial(self) -> Labels:
        """Return the non-colloquial labels."""
        return Labels(label for label in self._labels if not label.is_colloquial)

    @property
    def lower_case(self) -> Labels:
        """Return the labels in lower case."""
        return Labels(label.lower_case for label in self._labels)

    @property
    def spelling_alternatives(self) -> Labels:
        """Return the spelling alternatives for each label."""
        spelling_alternatives = [label.spelling_alternatives for label in self._labels]
        return Labels(chain(*spelling_alternatives))

    @property
    def first_spelling_alternatives(self) -> Labels:
        """Return the first spelling alternatives for each label."""
        return Labels(label.first_spelling_alternative for label in self._labels)

    @property
    def non_generated_spelling_alternatives(self) -> Labels:
        """Return the non-generated spelling alternatives for each label."""
        non_generated_spelling_alternatives = [label.non_generated_spelling_alternatives for label in self._labels]
        return Labels(chain(*non_generated_spelling_alternatives))

    @property
    def first_non_generated_spelling_alternatives(self) -> Labels:
        """Return the first non-generated spelling alternative for each label."""
        return Labels(first(label.non_generated_spelling_alternatives) for label in self._labels)

    @property
    def as_strings(self) -> tuple[str, ...]:
        """Return the labels as strings."""
        return tuple(str(label) for label in self._labels)
