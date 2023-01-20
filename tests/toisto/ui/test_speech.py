"""Unit tests for the text to speech."""

import unittest
from configparser import ConfigParser
from unittest.mock import patch, Mock

import gtts

from toisto.ui.speech import say


class SayTest(unittest.TestCase):
    """Unit tests for the say function."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = ConfigParser()
        self.config.add_section("commands")

    @patch("sys.platform", "darwin")
    @patch("gtts.gTTS.save", Mock(side_effect=gtts.tts.gTTSError))
    @patch("os.system")
    def test_google_translate_fails_on_mac_os(self, mock_os_system):
        """Test that the say program is called with the correct arguments, when Google Translate fails on MacOS."""
        self.config.set("commands", "mp3player", "afplay")
        say("nl", "Hallo", self.config)
        mock_os_system.assert_called_once_with("say --voice=Xander Hallo &")

    @patch("sys.platform", "windows")
    @patch("gtts.gTTS.save", Mock(side_effect=gtts.tts.gTTSError))
    def test_google_translate_fails_on_windows(self):
        """Test that the exception is not caught when Google Translate fails on Windows, because there is no plan B."""
        self.config.set("commands", "mp3player", "afplay")
        self.assertRaises(RuntimeError, say, "nl", "Hallo", self.config)

    @patch("gtts.gTTS.save", Mock())
    @patch("os.system")
    def test_system_call_afplay(self, mock_os_system):
        """Test that the afplay program is called with the correct arguments."""
        self.config.set("commands", "mp3player", "afplay")
        say("nl", "Hallo", self.config)
        mock_os_system.assert_called_once()
        self.assertTrue(mock_os_system.call_args_list[0][0][0].startswith("afplay "))

    @patch("gtts.gTTS.save", Mock())
    @patch("toisto.ui.speech.playsound")
    def test_call_playsound(self, mock_playsound):
        """Test that the playsound function is called."""
        self.config.set("commands", "mp3player", "playsound")
        say("nl", "Hallo", self.config)
        mock_playsound.assert_called_once()
