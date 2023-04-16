"""All languages as defined in the IANA language subtag registry."""

from typing import Final

from toisto.persistence.iana_language_subtag_registry import load_languages

IANA_LANGUAGE_SUBTAG_REGISTRY_URL: Final = "https://www.iana.org/assignments/language-subtag-registry"
ALL_LANGUAGES: Final = load_languages()
