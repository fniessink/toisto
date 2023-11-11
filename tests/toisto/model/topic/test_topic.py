"""Topic unit tests."""

import unittest

from toisto.model.topic.topic import Topic


class TopicTest(unittest.TestCase):
    """Unit tests for the topic class."""

    def test_composite_topic_with_own_concepts(self):
        """Test that a topic returns both its own concepts as well as concepts of subtopics."""
        Topic("fruit", frozenset(["apple", "pear"]))
        food = Topic("food", frozenset(["potato", "wine"]), frozenset(["fruit"]))
        self.assertEqual(frozenset(["apple", "pear", "potato", "wine"]), food.concepts)

    def test_composite_topic_without_own_concepts(self):
        """Test that a topic returns both its own concepts as well as concepts of subtopics."""
        Topic("fruit", frozenset(["apple", "pear"]))
        Topic("vegetables", frozenset(["cucumber", "tomato"]))
        food = Topic("food", topics=frozenset(["fruit", "vegetables"]))
        self.assertEqual(frozenset(["apple", "pear", "cucumber", "tomato"]), food.concepts)
