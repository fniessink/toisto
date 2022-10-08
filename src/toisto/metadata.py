"""Meta data about this application."""

from importlib.metadata import metadata, version

_metadata = metadata("Toisto")
NAME = _metadata["name"]
SUMMARY = _metadata["summary"]
VERSION = version(NAME)
