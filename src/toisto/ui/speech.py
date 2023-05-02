"""Text to speech."""

import sys
import tempfile
from configparser import ConfigParser
from subprocess import DEVNULL, Popen
from typing import Final

import gtts
from playsound import playsound

MAC_OS_SAY_VOICES: Final = dict(en="Daniel", fi="Satu", nl="Xander")


def _run_command(command: str, *args: str) -> None:
    """Run the command in the background and send output to /dev/null."""
    # Suppress the ruff message: "S603 `subprocess` call: check for execution of untrusted input". Popen should be
    # safe because it's invoked with either "say" or a mp3 play command provided by the user in the config file.
    Popen([command, *args], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)  # noqa: S603


def _say_with_macos_say(language: str, text: str, slow: bool) -> None:
    """Say the text with the MacOS say command."""
    voice = MAC_OS_SAY_VOICES[language]
    args = [f"--voice={voice}"]
    if slow:
        args.append("--rate=150")
    args.append(text.replace("'", r"\'"))
    _run_command("say", *args)


def _say_with_google_translate(language: str, text: str, config: ConfigParser, slow: bool) -> None:
    """Say the text with Google Translate say command."""
    try:
        service = gtts.gTTS(text=text, lang=language, slow=slow)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3_file:
            service.save(mp3_file.name)
    except gtts.tts.gTTSError as reason:
        message = f"Can't use Google Translate: {reason}"
        raise RuntimeError(message) from reason
    mp3_play_command = config.get("commands", "mp3player")
    if mp3_play_command == "playsound":
        playsound(mp3_file.name)
    else:
        _run_command(mp3_play_command, mp3_file.name)


def say(language: str, text: str, config: ConfigParser, slow: bool = False) -> None:
    """Say the text in the specified language."""
    try:
        _say_with_google_translate(language, text, config, slow)
    except RuntimeError:
        if sys.platform == "darwin":
            _say_with_macos_say(language, text, slow)
        else:
            raise
