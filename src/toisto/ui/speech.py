"""Text to speech."""

import os
import tempfile

import gtts


SAY_VOICES = dict(en="Daniel", fi="Satu", nl="Xander")


def _say_with_macos_say(language: str, text: str) -> None:
    """Say the text with the MacOS say command."""
    voice = SAY_VOICES[language]
    text = text.replace("'", r"\'")
    os.system(f"say --voice={voice} {text} &")


def _say_with_google_translate(language: str, text: str) -> None:
    """Say the text with Google Translate say command."""
    try:
        service = gtts.gTTS(text=text, lang=language)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3_file:
            service.save(mp3_file.name)
            os.system(f"afplay {mp3_file.name} &")
    except gtts.tts.gTTSError as reason:
        raise RuntimeError(f"Can't use Google Translate: {reason}") from reason


def say(language: str, text: str) -> None:
    """Say the text in the specified language."""
    try:
        _say_with_google_translate(language, text)
    except RuntimeError:
        _say_with_macos_say(language, text)
