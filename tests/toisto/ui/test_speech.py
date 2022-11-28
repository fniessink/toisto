"""Unit tests for the text to speech."""

import unittest
from unittest.mock import patch, Mock

import gtts

from toisto.ui.speech import say


class SayTest(unittest.TestCase):
    """Unit tests for the say function."""

    @patch("gtts.gTTS.save", Mock(side_effect=gtts.tts.gTTSError))
    @patch("os.system")
    def test_system_call_say(self, mock_os_system):
        """Test that the say program is called with the correct arguments."""
        say("nl", "Hallo")
        mock_os_system.assert_called_once_with("say --voice=Xander Hallo &")

    @patch("gtts.gTTS.save", Mock())
    @patch("os.system")
    def test_system_call_afplay(self, mock_os_system):
        """Test that the afplay program is called with the correct arguments."""
        say("nl", "Hallo")
        mock_os_system.assert_called_once()
        self.assertTrue(mock_os_system.call_args_list[0][0][0].startswith("afplay "))
