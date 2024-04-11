"""Load spelling alternatives."""

import re

from ..metadata import SPELLING_ALTERNATIVES_FILE
from ..model.language import LanguagePair
from ..model.language.label import Label
from .json_file import load_json


def load_spelling_alternatives(language_pair: LanguagePair) -> None:
    """Load the spelling alternatives."""
    spelling_alternatives = load_json(SPELLING_ALTERNATIVES_FILE)
    target, source = language_pair.target, language_pair.source
    key_language_mapping = {target: target, source: source, f"{source}-if-source-language": source}
    for key, language in key_language_mapping.items():
        for regexp, replacement in spelling_alternatives.get(key, {}).items():
            Label.ALTERNATIVES_TO_GENERATE.setdefault(language, {})[re.compile(regexp)] = replacement
