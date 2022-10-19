"""Entry classes."""

from dataclasses import dataclass
from typing import cast, Literal

from ..metadata import Language
from .quiz import Quiz


EntryDict = dict[Language, str | list[str]]
NounType = Literal["plural", "singular"]
NounEntryDict = dict[NounType, EntryDict]


@dataclass
class Entry:
    """Class representing a word or phrase from a topic."""

    entry: dict[Language, list[str]]

    def quizzes(self, language: Language, source_language: Language) -> list[Quiz]:
        """Generate the possible quizzes from the entry."""
        return (
            [Quiz(language, source_language, text, self.entry[source_language]) for text in self.entry[language]] +
            [Quiz(source_language, language, text, self.entry[language]) for text in self.entry[source_language]]
        )

    def has(self, *languages: Language) -> bool:
        """Return whether the entry has all the specified languages."""
        return all(language in self.entry for language in languages)

    def texts(self, language: Language) -> list[str]:
        """Return the texts for the language."""
        return self.entry[language]

    @classmethod
    def from_dict(cls, entry_dict: EntryDict) -> "Entry":
        """Instantiate an entry from a dict."""
        return cls({language: (text if isinstance(text, list) else [text]) for language, text in entry_dict.items()})


@dataclass
class NounEntry:
    """A noun with a singular and plural grammatical number.

    See https://en.wikipedia.org/wiki/Grammatical_number.
    """

    singular: Entry
    plural: Entry

    def quizzes(self, language: Language, source_language: Language) -> list[Quiz]:
        """Generate the possible quizzes from the entry."""
        result = []
        for entry in self.singular, self.plural:
            if entry.has(language, source_language):
                result.extend(entry.quizzes(language, source_language))
        singular_texts, plural_texts = self.singular.texts(language), self.plural.texts(language)
        result.extend([Quiz(language, language, text, plural_texts, "pluralize") for text in singular_texts])
        result.extend([Quiz(language, language, text, singular_texts, "singularize") for text in plural_texts])
        return result

    @classmethod
    def from_dict(cls, entry_dict: NounEntryDict) -> "NounEntry":
        """Instantiate an entry from a dict."""
        singular_entry = Entry.from_dict(entry_dict["singular"])
        plural_entry = Entry.from_dict(entry_dict["plural"])
        return cls(singular_entry, plural_entry)


def entry_factory(entry_dict: EntryDict | NounEntryDict) -> Entry | NounEntry:
    """Create an entry from the entry dict."""
    if "singular" in entry_dict and "plural" in entry_dict:
        return NounEntry.from_dict(cast(NounEntryDict, entry_dict))
    return Entry.from_dict(cast(EntryDict, entry_dict))
