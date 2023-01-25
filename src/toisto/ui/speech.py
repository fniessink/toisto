"""Text to speech."""

import os
import sys
import tempfile
from configparser import ConfigParser

import gtts
from playsound import playsound


SAY_VOICES = dict(en="Daniel", fi="Satu", nl="Xander")


def _say_with_macos_say(language: str, text: str, slow: bool = False) -> None:
    """Say the text with the MacOS say command."""
    voice = SAY_VOICES[language]
    rate = "--rate 150 " if slow else ""
    text = text.replace("'", r"\'")
    os.system(f"say --voice={voice} {rate}{text} &")


def _say_with_google_translate(language: str, text: str, config: ConfigParser, slow: bool = False) -> None:
    """Say the text with Google Translate say command."""
    try:
        service = gtts.gTTS(text=text, lang=language, slow=slow)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3_file:
            service.save(mp3_file.name)
    except gtts.tts.gTTSError as reason:
        raise RuntimeError(f"Can't use Google Translate: {reason}") from reason
    mp3_play_command = config.get("commands", "mp3player")
    if mp3_play_command == "playsound":
        playsound(mp3_file.name)
    else:
        os.system(f"{mp3_play_command} {mp3_file.name} &")


def say(language: str, text: str, config: ConfigParser, slow: bool = False) -> None:
    """Say the text in the specified language."""
    try:
        _say_with_google_translate(language, text, config, slow)
    except RuntimeError:
        if sys.platform == "darwin":
            _say_with_macos_say(language, text, slow)
        else:
            raise
