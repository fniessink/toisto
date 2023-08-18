"""Text matching."""

import string

# Translation table to remove punctuation from strings, except apostrophes.
WITHOUT_PUNCTUATION = str.maketrans("", "", string.punctuation)
del WITHOUT_PUNCTUATION[ord("'")]


def match(text1: str, *texts: str) -> bool:
    """Return whether the text matches any of the texts."""
    return any(
        text1.strip().translate(WITHOUT_PUNCTUATION) == text2.strip().translate(WITHOUT_PUNCTUATION) for text2 in texts
    )
