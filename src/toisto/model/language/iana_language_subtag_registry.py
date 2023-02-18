"""All languages as defined in the IANA language subtag registry."""

from toisto.persistence.iana_language_subtag_registry import load_languages

IANA_LANGUAGE_SUBTAG_REGISTRY_URL = "https://www.iana.org/assignments/language-subtag-registry"
ALL_LANGUAGES = load_languages()
