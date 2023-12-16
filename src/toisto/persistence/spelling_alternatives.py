"""Load spelling alternatives."""

import re

from ..metadata import SPELLING_ALTERNATIVES_FILE
from ..model.language import Language
from ..model.language.label import Label
from .json_file import load_json


def load_spelling_alternatives(target_language: Language, source_language: Language) -> None:
    """Load the spelling alternatives."""
    spelling_alternatives = load_json(SPELLING_ALTERNATIVES_FILE)
    key_language_mapping = {
        target_language: target_language,
        source_language: source_language,
        f"{source_language}-if-source-language": source_language,
    }
    for key, language in key_language_mapping.items():
        for regexp, replacement in spelling_alternatives.get(key, {}).items():
            Label.ALTERNATIVES_TO_GENERATE.setdefault(language, {})[re.compile(regexp)] = replacement
