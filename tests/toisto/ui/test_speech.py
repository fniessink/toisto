"""Unit tests for the text to speech."""

import unittest
from subprocess import DEVNULL  # nosec import_subprocess
from unittest.mock import Mock, patch

from gtts import gTTSError

from toisto.model.language import NL
from toisto.persistence.config import default_config
from toisto.ui.speech import Speech


class SayTest(unittest.TestCase):
    """Unit tests for the say function."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = default_config()

    @staticmethod
    def assert_popen_called_with(popen: Mock, *args: str) -> None:
        """Check that Popen was called with the given arguments."""
        popen.assert_called_once_with(list(args), stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)

    @patch("sys.platform", "darwin")
    @patch("toisto.ui.speech.gTTS", Mock(side_effect=gTTSError))
    @patch("toisto.ui.speech.run")
    @patch("toisto.ui.speech.Popen")
    def test_google_translate_fails_on_mac_os(self, popen: Mock, run: Mock) -> None:
        """Test that the say program is called with the correct arguments, when Google Translate fails on macOS."""
        run.return_value = available_voices = Mock()
        available_voices.stdout = ""
        self.config.set("commands", "mp3player", "afplay")
        Speech(self.config).say(NL, "Hallo")
        self.assert_popen_called_with(popen, "say", "-v", "Xander", "-r", "150", "Hallo")

    @patch("toisto.ui.speech.platform", Mock(return_value="ashell"))
    @patch("toisto.ui.speech.run")
    @patch("toisto.ui.speech.Popen")
    def test_always_use_apple_say_on_ashell(self, popen: Mock, run: Mock) -> None:
        """Test that the say program is called when running in a-Shell."""
        run.return_value = available_voices = Mock()
        available_voices.stdout = ""
        self.config.set("commands", "mp3player", "afplay")
        Speech(self.config).say(NL, "Hallo")
        self.assert_popen_called_with(popen, "say", "-v", "Xander", "Hallo")

    @patch("sys.platform", "darwin")
    @patch("toisto.ui.speech.gTTS", Mock(side_effect=gTTSError))
    @patch("toisto.ui.speech.run")
    @patch("toisto.ui.speech.Popen")
    def test_google_translate_fails_on_mac_os_twice(self, popen: Mock, run: Mock) -> None:
        """Test that the say program is called with the correct arguments, when Google Translate fails on macOS."""
        run.return_value = available_voices = Mock()
        available_voices.stdout = ""
        self.config.set("commands", "mp3player", "afplay")
        Speech(self.config).say(NL, "Hallo", slow=True)
        self.assert_popen_called_with(popen, "say", "-v", "Xander", "-r", "100", "Hallo")

    @patch("sys.platform", "windows")
    @patch("toisto.ui.speech.gTTS", Mock(side_effect=gTTSError))
    def test_google_translate_fails_on_windows(self) -> None:
        """Test that the exception is not caught when Google Translate fails on Windows, because there is no plan B."""
        self.config.set("commands", "mp3player", "afplay")
        self.assertRaises(RuntimeError, Speech(self.config).say, NL, "Hallo")

    @patch("toisto.ui.speech.gTTS", Mock())
    @patch("toisto.ui.speech.Popen")
    def test_system_call_afplay(self, popen: Mock) -> None:
        """Test that the afplay program is called with the correct arguments."""
        self.config.set("commands", "mp3player", "afplay")
        Speech(self.config).say(NL, "Hallo")
        popen.assert_called_once()
        self.assertEqual(popen.call_args_list[0][0][0][0], "afplay")

    @patch("toisto.ui.speech.music")
    def test_call_builtin_player(self, music: Mock) -> None:
        """Test that the bultin music player (Pygame) is called."""
        self.config.set("commands", "mp3player", "builtin")
        Speech(self.config).say(NL, "Hallo")
        music.queue.assert_called_once()

    @patch("sys.platform", "windows")
    @patch("toisto.ui.speech.music")
    def test_fail_to_import_pygame(self, music: Mock) -> None:
        """Test that an error is thrown if the builtin music player (Pygame) can't be used."""
        music.queue.side_effect = NameError
        self.config.set("commands", "mp3player", "builtin")
        self.assertRaises(RuntimeError, Speech(self.config).say, NL, "Hallo")

    @patch("toisto.ui.speech.platform", Mock(return_value="ashell"))
    @patch("toisto.ui.speech.run")
    @patch("toisto.ui.speech.Popen")
    def test_use_enhanced_voice_when_available(self, popen: Mock, run: Mock) -> None:
        """Test that the say program is called when running in a-Shell."""
        run.return_value = available_voices = Mock()
        available_voices.stdout = "Xander (Enhanced)"
        self.config.set("commands", "mp3player", "afplay")
        Speech(self.config).say(NL, "Hallo")
        self.assert_popen_called_with(popen, "say", "-v", "Xander (Enhanced)", "Hallo")
