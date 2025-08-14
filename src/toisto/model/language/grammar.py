"""Grammar types and models."""

from __future__ import annotations

from typing import Literal

GrammaticalGender = Literal["feminine", "masculine", "neuter"]
GrammaticalNumber = Literal["infinitive", "verbal noun", "singular", "plural"]
GrammaticalPerson = Literal["first person", "second person", "third person"]
DegreeOfComparison = Literal["positive degree", "comparative degree", "superlative degree"]
Diminutive = Literal["root", "diminutive"]
Tense = Literal["present tense", "past tense", "present perfect tense", "past perfect tense"]
GrammaticalMood = Literal["declarative", "interrogative", "imperative"]
GrammaticalPolarity = Literal["affirmative", "negative"]
Number = Literal["cardinal", "ordinal"]
Abbreviation = Literal["abbreviation", "full form"]
GrammaticalCategory = Literal[
    GrammaticalGender,
    GrammaticalNumber,
    GrammaticalPerson,
    DegreeOfComparison,
    Diminutive,
    Tense,
    GrammaticalMood,
    GrammaticalPolarity,
    Number,
    Abbreviation,
]


class GrammaticalForm:
    """Grammatical form of a label."""

    def __init__(self, grammatical_base: str = "", *grammatical_categories: GrammaticalCategory) -> None:
        self.grammatical_base = grammatical_base
        self.grammatical_categories = set(grammatical_categories)

    def __eq__(self, other: object) -> bool:
        """Return whether the grammatical forms are equal."""
        if isinstance(other, GrammaticalForm):
            return (
                self.grammatical_base == other.grammatical_base
                and self.grammatical_categories == other.grammatical_categories
            )
        return False

    def __ne__(self, other: object) -> bool:
        """Return whether the grammatical forms are not equal."""
        if isinstance(other, GrammaticalForm):
            return (
                self.grammatical_base != other.grammatical_base
                or self.grammatical_categories != other.grammatical_categories
            )
        return True

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(f"{self.grammatical_base}{sorted(self.grammatical_categories)}")

    def grammatical_differences(self, other: GrammaticalForm) -> set[GrammaticalCategory]:
        """Return the grammatical differences between this grammatical form and the other form."""
        return other.grammatical_categories.difference(self.grammatical_categories)
