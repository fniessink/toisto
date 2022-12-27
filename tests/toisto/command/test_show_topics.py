"""Unit tests for the show topics command."""

from unittest.mock import patch

from toisto.command import show_topics
from toisto.model import Topic, Topics

from ..base import ToistoTestCase


class ShowTopicsTest(ToistoTestCase):
    """Test the show topics command."""

    def setUp(self):
        """Set up test fixtures."""
        self.quiz = self.create_quiz("hello", "fi", "nl", "Terve", ["Hoi"])
        self.topics = Topics(set([Topic("topic", (), set([self.quiz]))]))

    def test_title(self):
        """Test the table title."""
        with patch("rich.console.Console.print") as console_print:
            show_topics("fi", "nl", self.topics)
        self.assertEqual("Topic topic", console_print.call_args[0][0].title)
