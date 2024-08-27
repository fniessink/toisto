"""Unit tests for the text to speech."""

import unittest
from subprocess import DEVNULL  # nosec import_subprocess
from unittest.mock import Mock, patch

from gtts import gTTSError

from toisto.persistence.config import default_config
from toisto.ui.speech import say


class SayTest(unittest.TestCase):
    """Unit tests for the say function."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = default_config()

    @patch("sys.platform", "darwin")
    @patch("toisto.ui.speech.gTTS", Mock(side_effect=gTTSError))
    @patch("toisto.ui.speech.Popen")
    def test_google_translate_fails_on_mac_os(self, mock_subprocess_popen: Mock) -> None:
        """Test that the say program is called with the correct arguments, when Google Translate fails on MacOS."""
        self.config.set("commands", "mp3player", "afplay")
        say("nl", "Hallo", self.config)
        mock_subprocess_popen.assert_called_once_with(
            ["say", "--voice=Xander (Enhanced)", "Hallo"],
            stdin=DEVNULL,
            stdout=DEVNULL,
            stderr=DEVNULL,
        )

    @patch("sys.platform", "darwin")
    @patch("toisto.ui.speech.gTTS", Mock(side_effect=gTTSError))
    @patch("toisto.ui.speech.Popen")
    def test_google_translate_fails_on_mac_os_twice(self, mock_subprocess_popen: Mock) -> None:
        """Test that the say program is called with the correct arguments, when Google Translate fails on MacOS."""
        self.config.set("commands", "mp3player", "afplay")
        say("nl", "Hallo", self.config, slow=True)
        mock_subprocess_popen.assert_called_once_with(
            ["say", "--voice=Xander (Enhanced)", "--rate=150", "Hallo"],
            stdin=DEVNULL,
            stdout=DEVNULL,
            stderr=DEVNULL,
        )

    @patch("sys.platform", "windows")
    @patch("toisto.ui.speech.gTTS", Mock(side_effect=gTTSError))
    def test_google_translate_fails_on_windows(self) -> None:
        """Test that the exception is not caught when Google Translate fails on Windows, because there is no plan B."""
        self.config.set("commands", "mp3player", "afplay")
        self.assertRaises(RuntimeError, say, "nl", "Hallo", self.config)

    @patch("toisto.ui.speech.gTTS", Mock())
    @patch("toisto.ui.speech.Popen")
    def test_system_call_afplay(self, mock_subprocess_popen: Mock) -> None:
        """Test that the afplay program is called with the correct arguments."""
        self.config.set("commands", "mp3player", "afplay")
        say("nl", "Hallo", self.config)
        mock_subprocess_popen.assert_called_once()
        self.assertEqual(mock_subprocess_popen.call_args_list[0][0][0][0], "afplay")

    @patch("toisto.ui.speech.music")
    def test_call_builtin_player(self, mock_music: Mock) -> None:
        """Test that the bultin music player (Pygame) is called."""
        self.config.set("commands", "mp3player", "builtin")
        say("nl", "Hallo", self.config)
        mock_music.queue.assert_called_once()

    @patch("sys.platform", "windows")
    @patch("toisto.ui.speech.music")
    def test_fail_to_import_pygame(self, mock_music: Mock) -> None:
        """Test that an error is thrown if the builtin music player (Pygame) can't be used."""
        mock_music.queue.side_effect = NameError
        self.config.set("commands", "mp3player", "builtin")
        self.assertRaises(RuntimeError, say, "nl", "Hallo", self.config)
