"""Unit tests for the show topics command."""

from unittest.mock import MagicMock, Mock, patch

from toisto.command.show_topics import show_topics
from toisto.model.language import Language
from toisto.model.language.concept_factory import create_concept
from toisto.model.quiz.quiz_factory import create_quizzes

from ...base import ToistoTestCase


class ShowTopicsTest(ToistoTestCase):
    """Test the show topics command."""

    def setUp(self):
        """Set up test fixtures."""
        concept = create_concept("hello", dict(fi="Terve", nl="Hoi"), topic="topic")
        self.quiz = create_quizzes("fi", "nl", concept).by_quiz_type("read").pop()
        self.concepts = {concept}

    @patch("rich.console.Console.pager", MagicMock())
    def show_topics(self, target_language: Language | None = None, source_language: Language | None = None) -> Mock:
        """Run the show topics command."""
        with patch("rich.console.Console.print") as console_print:
            show_topics(target_language or Language("fi"), source_language or Language("nl"), self.concepts)
        return console_print

    def test_title(self):
        """Test the table title."""
        console_print = self.show_topics()
        self.assertEqual("Topic topic", console_print.call_args[0][0].title)
        self.assertEqual(1, console_print.call_args_list[0][0][0].row_count)

    def test_contents(self):
        """Test that the table contains the concept."""
        console_print = self.show_topics()
        self.assertEqual(1, console_print.call_args_list[0][0][0].row_count)

    def test_skip_concepts_without_labels_in_the_selected_languages(self):
        """Test that concepts without labels in the target or source language are not shown."""
        console_print = self.show_topics("en", "fr")
        self.assertEqual(0, console_print.call_args_list[0][0][0].row_count)
