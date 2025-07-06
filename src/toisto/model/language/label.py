"""Labels."""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from functools import cached_property
from itertools import chain
from random import shuffle
from typing import ClassVar

from toisto.tools import first, first_upper

from . import Language

SpellingAlternatives = dict[Language, dict[re.Pattern[str], str]]

END_OF_SENTENCE_PUNCTUATION = "?!."


class Label:
    """Class representing labels for concepts."""

    __slots__ = (
        "__dict__",
        "_roots",
        "_values",
        "colloquial",
        "language",
        "notes",
        "tip",
    )  # Without adding __dict__ to slots @cached_property does not work

    ALTERNATIVES_TO_GENERATE: ClassVar[SpellingAlternatives] = {}  # These are loaded upon start of the application

    instances: ClassVar[dict[str, Label]] = {}

    def __init__(  # noqa: PLR0913
        self,
        language: Language,
        value: str | list[str],
        notes: tuple[str, ...] = (),
        roots: tuple[str, ...] = (),
        tip: str = "",
        *,
        colloquial: bool = False,
    ) -> None:
        """Initialize the label."""
        self.language = language
        self._values = value if isinstance(value, list) else [value]
        self.notes = notes
        self._roots = roots
        self.tip = tip
        self.colloquial = colloquial
        self.instances[self._values[0]] = self

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
        return any(self._values)

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(f"{self.language}{self}")

    def __str__(self) -> str:
        """Return the label string value."""
        return self._values[0]

    __repr__ = __str__

    def copy(self, value: str) -> Label:
        """Return a copy of this label with a different value."""
        return Label(self.language, value, self.notes, self._roots, self.tip, colloquial=self.colloquial)

    @property
    def non_generated_spelling_alternatives(self) -> Labels:
        """Extract the spelling alternatives from the label."""
        return Labels([self.copy(value) for value in self._values])

    @cached_property
    def spelling_alternatives(self) -> Labels:
        """Extract the spelling alternatives from the label and generate additional spelling alternatives."""
        alternatives = self.non_generated_spelling_alternatives
        generated_alternatives = set()
        for alternative in alternatives:
            for pattern, replacement in self.ALTERNATIVES_TO_GENERATE.get(self.language, {}).items():
                if re.search(pattern, str(alternative)):
                    generated_alternative = self.copy(re.sub(pattern, replacement, str(alternative)))
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
        return self.copy(" ".join(words))

    @property
    def with_upper_case_first_letter(self) -> Label:
        """Return the label with the first letter upper cased."""
        return self.copy(first_upper(self._values[0]))

    @property
    def lower_case(self) -> Label:
        """Return the label in lower case."""
        return self.copy(self._values[0].lower())

    @property
    def is_complete_sentence(self) -> bool:
        """Return whether this is a complete sentence (starts with an upper case letter and ends with punctuation)."""
        return self.starts_with_upper_case and self.ends_with_punctuation

    @property
    def starts_with_upper_case(self) -> bool:
        """Return whether the label starts with an upper case letter."""
        return self._values[0][0].isupper()

    @property
    def ends_with_punctuation(self) -> bool:
        """Return whether the label ends with punctuation."""
        return str(self._values[0])[-1] in END_OF_SENTENCE_PUNCTUATION

    @property
    def pronounceable(self) -> str:
        """Return the label as text that can be sent to a speech synthesizer."""
        return self._values[0].replace("'", "").replace("-", " ")

    @property
    def word_count(self) -> int:
        """Return the label word count."""
        return len(str(self.first_spelling_alternative).split(" "))

    @property
    def roots(self) -> Labels:
        """Return the label roots."""
        roots = []
        for root in self._roots:
            root_label = self.instances[root]
            roots.extend([root_label, *root_label.roots])
        return Labels(roots)

    @property
    def compounds(self) -> Labels:
        """Return the label compounds."""
        return Labels([label for label in self.instances.values() if self in label.roots])


class Labels:  # noqa: PLW1641
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
        return Labels(label for label in self._labels if not label.colloquial)

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
    def compounds(self) -> Labels:
        """Return the compounds of the labels."""
        compounds = [label.compounds for label in self._labels]
        return Labels(chain(*compounds))

    @property
    def as_strings(self) -> tuple[str, ...]:
        """Return the labels as strings."""
        return tuple(str(label) for label in self._labels)
