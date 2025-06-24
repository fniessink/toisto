"""Text to speech."""

from __future__ import annotations

import tempfile
from configparser import ConfigParser
from contextlib import redirect_stderr, redirect_stdout, suppress
from functools import cached_property
from subprocess import DEVNULL, Popen, run  # nosec import_subprocess

from gtts import gTTS, gTTSError

with suppress(ModuleNotFoundError), redirect_stderr(None), redirect_stdout(None):
    from pygame.mixer import music

from toisto.model.language import EN, FI, NL, Language
from toisto.tools import platform


def _run_command(command: str, *args: str) -> None:
    """Run the command in the background and send any output to /dev/null."""
    # Suppress the ruff message: "S603 `subprocess` call: check for execution of untrusted input" and the bandit
    # message: "[B603:subprocess_without_hell_equals_true] subprocess call - check for execution of untrusted input".
    # Popen should be safe as it is invoked with either "say" or an mp3 play command provided by the user in their
    # config file.
    Popen([command, *args], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)  # noqa: S603, # nosec subprocess_without_shell_equals_true


class Speech:
    """Text to speech."""

    def __init__(self, config: ConfigParser) -> None:
        self.config = config
        self.platform = platform()

    def say(self, language: Language, text: str, slow: bool = False) -> None:
        """Say the text in the specified language."""
        if self.platform == "ashell":
            return self._say_with_apple_say(language, text, slow)
        try:
            self._say_with_google_translate(language, text, slow)
        except RuntimeError:
            if self.platform == "darwin":
                self._say_with_apple_say(language, text, slow)
            else:
                raise

    def _say_with_apple_say(self, language: Language, text: str, slow: bool) -> None:
        """Say the text with the Apple say command that's available on macOS and iOS."""
        voice_arg = ["-v", self.apple_say_voices[language]]
        # On iOS the argument for --rate/-r is not words per minute like on the Mac, but something else:
        ashell = self.platform == "ashell"
        if slow:  # noqa: SIM108
            rate_arg = ["-r", "30000"] if ashell else ["-r", "100"]
        else:
            rate_arg = [] if ashell else ["-r", "150"]
        args = voice_arg + rate_arg + [text.replace("'", r"\'")]
        _run_command("say", *args)

    def _say_with_google_translate(self, language: Language, text: str, slow: bool) -> None:
        """Say the text with Google Translate say command."""
        try:
            service = gTTS(text=text, lang=str(language), lang_check=False, slow=slow)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3_file:
                service.save(mp3_file.name)
        except gTTSError as reason:
            message = f"Can't use Google Translate: {reason}"
            raise RuntimeError(message) from reason
        self._play_mp3(mp3_file)

    def _play_mp3(self, mp3_file: tempfile._TemporaryFileWrapper[bytes]) -> None:
        """Play the MP3 file."""
        mp3_play_command = self.config.get("commands", "mp3player")
        if mp3_play_command == "builtin":
            try:
                music.queue(mp3_file.name)
            except NameError as error:
                message = "Can't use builtin (Pygame) music player on this platform"
                raise RuntimeError(message) from error
        else:
            _run_command(mp3_play_command, mp3_file.name)

    @cached_property
    def apple_say_voices(self) -> dict[Language, str]:
        """Return the best available voices."""
        available_voices = run(["say", "-v", "?"], capture_output=True, check=False, text=True).stdout  # noqa: S607, # nosec subprocess_without_shell_equals_true, start_process_with_partial_path
        voices = {}
        for language, voice in {EN: "Daniel", FI: "Satu", NL: "Xander"}.items():
            enhanced_voice = f"{voice} (Enhanced)"
            voices[language] = enhanced_voice if enhanced_voice in available_voices else voice
        return voices
