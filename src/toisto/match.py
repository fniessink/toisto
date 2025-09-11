"""Text matching."""

import string

# Translation table to remove punctuation from strings, except apostrophes and hyphens.
WITHOUT_PUNCTUATION = str.maketrans("", "", string.punctuation)
for char in ["'", "-"]:
    del WITHOUT_PUNCTUATION[ord(char)]


def match(text1: str, *texts: str, case_sensitive: bool = True) -> bool:
    """Return whether the text matches any of the texts."""
    if not case_sensitive:
        text1 = text1.lower()
        texts = tuple(text.lower() for text in texts)
    return any(
        text1.strip().translate(WITHOUT_PUNCTUATION) == text2.strip().translate(WITHOUT_PUNCTUATION) for text2 in texts
    )
