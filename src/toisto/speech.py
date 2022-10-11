"""Text to speech."""

import os

VOICES = dict(fi="Satu", nl="Xander")


def say(language: str, text: str) -> None:
    """Say the text in the specified language."""
    voice = VOICES[language]
    text = text.replace("'", r"\'")
    os.system(f"say --voice={voice} --interactive=bold {text}")
