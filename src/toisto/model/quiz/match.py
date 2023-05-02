"""Text matching."""

import string

# Translation table to remove punctuation (including whitespace) from strings, except apostrophes.
WITHOUT_PUNCTUATION = str.maketrans("", "", string.punctuation + string.whitespace)
del WITHOUT_PUNCTUATION[ord("'")]


def match(text1: str, *texts: str) -> bool:
    """Return whether the text matches any of the texts."""
    return any(text1.translate(WITHOUT_PUNCTUATION) == text2.translate(WITHOUT_PUNCTUATION) for text2 in texts)
