"""Language package."""

from dataclasses import dataclass
from typing import Final, NewType

Language = NewType("Language", str)

EN: Final[Language] = Language("en")
FI: Final[Language] = Language("fi")
NL: Final[Language] = Language("nl")


@dataclass
class LanguagePair:
    """Target and source language pair."""

    target: Language
    source: Language
