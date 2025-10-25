"""Grammatical form."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .grammatical_category import GrammaticalCategory

if TYPE_CHECKING:
    from .label import Label


class GrammaticalForm:
    """Grammatical form of a label."""

    def __init__(self, grammatical_base: str = "", /, *grammatical_categories: GrammaticalCategory) -> None:
        self.grammatical_base = grammatical_base  # Base form of a label, for example "table" is the base of "tables"
        self.grammatical_categories = frozenset(grammatical_categories)
        self.other_grammatical_categories: dict[GrammaticalCategory, Label] = {}

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
        return hash(f"{self.grammatical_base}{sorted(str(category) for category in self.grammatical_categories)}")

    def grammatical_differences(self, other: GrammaticalForm) -> frozenset[GrammaticalCategory]:
        """Return the grammatical differences between this grammatical form and the other form."""
        return other.grammatical_categories.difference(self.grammatical_categories)
