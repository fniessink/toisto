"""Link words to an online dictionary."""

from string import punctuation


def linkify_and_enumerate(*texts: str, sep: str = ", ") -> str:
    """Return a linkified and enumerated version of the texts."""
    return sep.join(f'"{linkify(text)}"' for text in texts)


def linkify(text: str) -> str:
    """Return a version of the text where each word is turned into a link to a dictionary."""
    linkified_words = []
    for word in text.split():
        prefix, word, postfix = split_punctuation(word)
        linkified_words.append(f"{prefix}[link=https://en.wiktionary.org/wiki/{word.lower()}]{word}[/link]{postfix}")
    return " ".join(linkified_words)


def split_punctuation(text: str) -> tuple[str, str, str]:
    """Return a tuple of prefixed punctuation, the text without punctuation, and postfix punctuation."""
    stripped_text = text.strip(punctuation)
    stripped_text_start = text.find(stripped_text)
    stripped_text_end = stripped_text_start + len(stripped_text)
    return text[:stripped_text_start], text[stripped_text_start:stripped_text_end], text[stripped_text_end:]
