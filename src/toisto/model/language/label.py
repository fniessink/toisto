"""Labels."""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from difflib import SequenceMatcher
from functools import cached_property
from itertools import chain
from random import shuffle
from typing import ClassVar

from toisto.match import match
from toisto.tools import first, first_upper, unique

from . import Language
from .grammatical_category import GrammaticalCategory
from .grammatical_form import GrammaticalForm

SpellingAlternatives = dict[Language, dict[re.Pattern[str], str]]
HomonymMapping = dict[tuple[Language, str], list["Label"]]


class Label:
    """Class representing labels for concepts."""

    END_OF_SENTENCE_PUNCTUATION = "?!."
    ALTERNATIVES_TO_GENERATE: ClassVar[SpellingAlternatives] = {}  # These are loaded upon start of the application

    homograph_mapping: ClassVar[HomonymMapping] = {}
    capitonym_mapping: ClassVar[HomonymMapping] = {}

    def __init__(  # noqa: PLR0913
        self,
        language: Language,
        value: str | list[str],
        grammatical_form: GrammaticalForm | None = None,
        notes: tuple[str, ...] = (),
        roots: tuple[str, ...] = (),
        tips: tuple[str, ...] = (),
        cloze_tests: tuple[str, ...] = (),
        *,
        colloquial: bool = False,
        meaning_only: bool = False,
    ) -> None:
        """Initialize the label."""
        self.language = language
        self._values = value if isinstance(value, list) else [value]
        self.grammatical_form = grammatical_form or GrammaticalForm()
        self.notes = notes
        self._roots = roots
        self.tips = tips
        self._cloze_tests = cloze_tests
        self.colloquial = colloquial
        self.meaning_only = meaning_only
        for spelling_alternative in self._values:
            self.homograph_mapping.setdefault((language, spelling_alternative), []).append(self)
            self.capitonym_mapping.setdefault((language, spelling_alternative.lower()), []).append(self)

    def __eq__(self, other: object) -> bool:
        """Return whether the labels are equal."""
        if isinstance(other, Label):
            return (
                self.language == other.language
                and str(self) == str(other)
                and self.grammatical_form == other.grammatical_form
            )
        return False

    def __ne__(self, other: object) -> bool:
        """Return whether the labels are not equal."""
        if isinstance(other, Label):
            return (
                self.language != other.language
                or str(self) != str(other)
                or self.grammatical_form != other.grammatical_form
            )
        return True

    def __bool__(self) -> bool:
        """Return whether the label is empty or not."""
        return any(self._values)

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(f"{self.language}{self}")

    def __str__(self) -> str:
        """Return the label string value of the first spelling alternative."""
        return self._values[0]

    __repr__ = __str__

    def copy(self, value: str) -> Label:
        """Return a copy of this label with a different value."""
        if value == self._values[0]:
            return self
        return Label(
            self.language,
            value,
            self.grammatical_form,
            self.notes,
            self._roots,
            self.tips,
            colloquial=self.colloquial,
            meaning_only=self.meaning_only,
        )

    @cached_property
    def non_generated_spelling_alternatives(self) -> Labels:
        """Return the spelling alternatives, excluding generated alternatives, as separate labels."""
        return Labels(self.copy(value) for value in self._values)

    @cached_property
    def generated_spelling_alternatives(self) -> Labels:
        """Generate additional spelling alternatives."""
        generated_alternatives = set()
        for alternative in self.non_generated_spelling_alternatives:
            for pattern, replacement in self.ALTERNATIVES_TO_GENERATE.get(self.language, {}).items():
                if re.search(pattern, str(alternative)):
                    value = re.sub(pattern, replacement, str(alternative))
                    if alternative.starts_with_upper_case:
                        value = first_upper(value)
                    generated_alternatives.add(self.copy(value))
        return Labels(generated_alternatives)

    @property
    def spelling_alternatives(self) -> Labels:
        """Extract the spelling alternatives from the label and generate additional spelling alternatives."""
        return self.non_generated_spelling_alternatives + self.generated_spelling_alternatives

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
        return str(self._values[0])[-1] in self.END_OF_SENTENCE_PUNCTUATION

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
        roots: list[Label] = []
        for root in self._roots:
            root_labels = self.homograph_mapping[(self.language, root)]
            roots.extend(root_labels)
            for root_label in root_labels:
                roots.extend(root_label.roots)
        return Labels(roots)

    @property
    def compounds(self) -> Labels:
        """Return the label compounds."""
        return Labels(label for label in chain(*self.homograph_mapping.values()) if self in label.roots)

    @cached_property
    def cloze_tests(self) -> Labels:
        """Return the cloze tests."""
        return Labels(Label(self.language, cloze_test) for cloze_test in self._cloze_tests)

    @property
    def is_grammatical_base(self) -> bool:
        """Return whether this label has the grammatical base form."""
        return str(self) == self.grammatical_form.grammatical_base

    def has_same_grammatical_form(self, other: Label) -> bool:
        """Return whether this label has the same grammatical form as the other label."""
        self_grammatical_categories = self.grammatical_form.grammatical_categories
        other_grammatical_categories = other.grammatical_form.grammatical_categories
        return (
            self_grammatical_categories == other_grammatical_categories
            or (not self_grammatical_categories and other.is_grammatical_base)
            or (not other_grammatical_categories and self.is_grammatical_base)
        )

    def has_same_grammatical_base(self, other: Label) -> bool:
        """Return whether this label has the same grammatical base as the other label."""
        return self.grammatical_form.grammatical_base == other.grammatical_form.grammatical_base

    def grammatical_differences(self, *labels: Label) -> frozenset[GrammaticalCategory]:
        """Return the grammatical differences between this label and the other labels."""
        differences: set[GrammaticalCategory] = set()
        for label in labels:
            differences |= label.grammatical_form.grammatical_differences(self.grammatical_form)
        return frozenset(differences)

    def is_homograph(self, other: Label) -> bool:
        """Return whether this label and the other label are homographs."""
        return self.language == other.language and str(self) == str(other)

    @property
    def homographs(self) -> Labels:
        """Return the homographs of this label."""
        return Labels(label for label in self.homograph_mapping[(self.language, str(self))] if self is not label)

    @property
    def capitonyms(self) -> Labels:
        """Return the capitonyms of this label."""
        capitonym_key = (self.language, str(self).lower())
        return Labels(label for label in self.capitonym_mapping[capitonym_key] if not self.is_homograph(label))

    def similarity(self, text: str) -> float:
        """Return the similarity between this label and the text as float in the range [0, 1].

        A similarity of 1 means the label and text are equal and 0 means they are completely different.
        """
        return SequenceMatcher(a=str(self).lower(), b=text.lower()).ratio()

    def register_other_grammatical_categories(self, labels: Labels) -> None:
        """Register the other grammatical forms of this label."""
        for label in labels.with_language(self.language).with_same_grammatical_base(self):
            grammatical_differences = label.grammatical_differences(self)
            if len(grammatical_differences) == 1:
                self.grammatical_form.other_grammatical_categories[first(grammatical_differences)] = label


class Labels:  # noqa: PLW1641
    """Labels collection."""

    def __init__(self, labels: Iterable[Label] = ()) -> None:
        self._labels = tuple(labels)

    def __repr__(self) -> str:
        """Return the string representation of the labels."""
        return repr(tuple(repr(label) for label in self))

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

    def __getattr__(self, attribute: str) -> Label:
        """Return the label with the given string value. Used in unit tests."""
        return first([label for label in self if str(label).lower().replace(" ", "_") == attribute])

    def __getitem__(self, index: int) -> Label:
        """Return the Label at the specified position."""
        return self._labels[index]

    def __len__(self) -> int:
        """Return the number of labels."""
        return len(self._labels)

    def with_language(self, language: Language) -> Labels:
        """Return the labels with the specified language."""
        return Labels(label for label in self if label.language == language)

    def with_same_grammatical_categories_as(self, other: Label) -> Labels:
        """Return the labels with the specified grammatical categories."""
        return Labels(label for label in self if label.has_same_grammatical_form(other))

    def with_same_grammatical_base(self, other: Label) -> Labels:
        """Return the labels with the specified grammatical categories."""
        return Labels(label for label in self if label.has_same_grammatical_base(other))

    def most_similar_label(self, text: str, min_similarity: float = 0.6) -> Label | None:
        """Return the label most similar to the text that has at least the minimum simularity."""
        if similar_labels := [label for label in self if label.similarity(text) >= min_similarity]:
            return sorted(similar_labels, key=lambda label: label.similarity(text))[-1]
        return None

    def matching(self, text: str, *, case_sensitive: bool = True) -> Labels:
        """Return the labels that match the text."""
        return Labels(
            label
            for label in self
            if match(text, *label.spelling_alternatives.as_strings, case_sensitive=case_sensitive)
        )

    def register_other_grammatical_categories(self) -> None:
        """For each label, register other grammatical forms of that label."""
        for label in self:
            label.register_other_grammatical_categories(self)

    @property
    def non_colloquial(self) -> Labels:
        """Return the non-colloquial labels."""
        return Labels(label for label in self if not label.colloquial)

    @property
    def not_meaning_only(self) -> Labels:
        """Return the labels that are not meaning-only."""
        return Labels(label for label in self if not label.meaning_only)

    @property
    def spelling_alternatives(self) -> Labels:
        """Return the spelling alternatives for each label."""
        spelling_alternatives = [label.spelling_alternatives for label in self]
        return Labels(chain(*spelling_alternatives))

    @property
    def first_spelling_alternatives(self) -> Labels:
        """Return the first spelling alternatives for each label."""
        return Labels(label.first_spelling_alternative for label in self)

    @property
    def non_generated_spelling_alternatives(self) -> Labels:
        """Return the non-generated spelling alternatives for each label."""
        non_generated_spelling_alternatives = [label.non_generated_spelling_alternatives for label in self]
        return Labels(chain(*non_generated_spelling_alternatives))

    @property
    def first_non_generated_spelling_alternatives(self) -> Labels:
        """Return the first non-generated spelling alternative for each label."""
        return Labels(first(label.non_generated_spelling_alternatives) for label in self)

    @property
    def compounds(self) -> Labels:
        """Return the compounds of the labels."""
        return Labels(chain(*[label.compounds for label in self]))

    @property
    def cloze_tests(self) -> Labels:
        """Return the cloze tests of the labels."""
        return Labels(chain(*[label.cloze_tests for label in self]))

    @property
    def as_strings(self) -> tuple[str, ...]:
        """Return the labels as strings, without duplicates."""
        return tuple(unique(str(label) for label in self))
