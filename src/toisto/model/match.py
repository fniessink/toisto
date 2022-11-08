"""Text matching."""

import string


def without_punctuation(text: str) -> str:
    """Remove text without punctuation."""
    return ''.join(char for char in text if char not in string.punctuation)


def match(text1: str, *texts: str) -> bool:
    """Return whether the text matches any of the texts."""
    return any(
        without_punctuation(text1.strip().lower()) == without_punctuation(text2.strip().lower()) for text2 in texts
    )
