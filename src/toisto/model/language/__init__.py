"""Language package."""

from dataclasses import dataclass
from typing import NewType

Language = NewType("Language", str)


@dataclass
class LanguagePair:
    """Target and source language pair."""

    target: Language
    source: Language
