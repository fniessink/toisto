"""Unit tests for the model filter."""

import unittest
from argparse import ArgumentParser
from unittest.mock import Mock, patch

from toisto.model.filter import filter_concepts
from toisto.model.language.concept import ConceptId
from toisto.model.language.concept_factory import create_concept
from toisto.model.topic.topic import Topic


class FilterTest(unittest.TestCase):
    """Unit tests for the filter method."""

    def setUp(self):
        """Set up the unit test fixtures."""
        self.argument_parser = ArgumentParser()
        self.foo = create_concept("foo", {})
        self.bar = create_concept("bar", {})
        self.concepts = {self.foo, self.bar}
        self.topic_name = "bar"
        self.topic = Topic(self.topic_name, frozenset([ConceptId("bar")]), frozenset())

    def test_no_concepts_and_no_filter(self):
        """Test no concepts and no filters."""
        self.assertEqual(set(), filter_concepts(set(), set(), [], [], self.argument_parser))

    def test_concepts_but_no_filters(self):
        """Test that all concepts are returned."""
        self.assertEqual(self.concepts, filter_concepts(self.concepts, set(), [], [], self.argument_parser))

    def test_selected_concepts(self):
        """Test that the selected concepts are returned."""
        self.assertEqual({self.bar}, filter_concepts(self.concepts, set(), ["bar"], [], self.argument_parser))

    def test_selected_topics(self):
        """Test that the selected concepts are returned."""
        topics = {self.topic}
        selected_topics = [self.topic_name]
        self.assertEqual({self.bar}, filter_concepts(self.concepts, topics, [], selected_topics, self.argument_parser))

    @patch("sys.stderr.write")
    def test_selected_concepts_without_concepts(self, sys_stderr_write: Mock):
        """Test that an empty selection results in an error message."""
        self.assertRaises(SystemExit, filter_concepts, self.concepts, set(), ["baz"], [], self.argument_parser)
        self.assertIn("Concept 'baz' not found", sys_stderr_write.call_args_list[1][0][0])

    @patch("sys.stderr.write")
    def test_selected_topic_does_not_exist(self, sys_stderr_write: Mock):
        """Test that an empty selection results in an error message."""
        self.assertRaises(SystemExit, filter_concepts, self.concepts, set(), [], ["topic"], self.argument_parser)
        self.assertIn("Topic 'topic' not found\n", sys_stderr_write.call_args_list[1][0][0])

    @patch("sys.stderr.write")
    def test_one_selected_topic_does_not_exist(self, sys_stderr_write: Mock):
        """Test that an empty selection results in an error message."""
        topics = {self.topic}
        selected_topics = [self.topic_name, "other topic"]
        self.assertRaises(SystemExit, filter_concepts, self.concepts, topics, [], selected_topics, self.argument_parser)
        self.assertIn("Topic 'other topic' not found\n", sys_stderr_write.call_args_list[1][0][0])

    @patch("sys.stderr.write")
    def test_no_concepts_with_topic_found(self, sys_stderr_write: Mock):
        """Test that an empty selection results in an error message."""
        concepts = {self.foo}
        topics = {self.topic}
        selected_topics = [self.topic_name]
        self.assertRaises(SystemExit, filter_concepts, concepts, topics, [], selected_topics, self.argument_parser)
        self.assertIn(f"No concepts with topic '{self.topic_name}' found\n", sys_stderr_write.call_args_list[1][0][0])
