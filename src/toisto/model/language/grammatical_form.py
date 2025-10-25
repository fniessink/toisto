"""Grammatical form."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .grammatical_category import GrammaticalCategory

if TYPE_CHECKING:
    from .label import Label


class GrammaticalForm:  # noqa: PLW1641
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

    def grammatical_differences(self, other: GrammaticalForm) -> frozenset[GrammaticalCategory]:
        """Return the grammatical differences between this grammatical form and the other form."""
        return other.grammatical_categories.difference(self.grammatical_categories)
