"""Unit tests for the text to speech."""

import unittest
from unittest.mock import patch

from toisto.speech import say


class SayTest(unittest.TestCase):
    """Unit tests for the say function."""

    @patch("os.system")
    def test_system_call(self, mock_os_system):
        """Test that the say program is called with the correct arguments."""
        say("nl", "Hallo")
        mock_os_system.assert_called_once_with("say --voice=Xander --interactive=bold 'Hallo'")
