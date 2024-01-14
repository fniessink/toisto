"""Unit tests for the model filter."""

from argparse import ArgumentParser
from typing import NoReturn
from unittest.mock import Mock, patch

from toisto.model.filter import filter_concepts
from toisto.model.language import Language
from toisto.model.language.concept import Concept, ConceptId
from toisto.model.language.concept_factory import create_concept

from ...base import ToistoTestCase


class FilterTest(ToistoTestCase):
    """Unit tests for the filter method."""

    def setUp(self):
        """Set up the unit test fixtures."""
        super().setUp()
        self.argument_parser = ArgumentParser()
        self.foo = create_concept("foo", {})
        self.bar = create_concept("bar", {})
        self.concepts = {self.foo, self.bar}

    def filter_concepts(
        self,
        *,
        concepts: set[Concept] | None = None,
        selected_concepts: list[ConceptId] | None = None,
    ) -> set[Concept] | NoReturn:
        """Filter the concepts."""
        return filter_concepts(
            self.concepts if concepts is None else concepts,
            selected_concepts or [],
            Language("en"),
            self.argument_parser,
        )

    def test_no_concepts_and_no_filter(self):
        """Test no concepts and no filters."""
        self.assertEqual(set(), self.filter_concepts(concepts=set()))

    def test_concepts_but_no_filters(self):
        """Test that all concepts are returned."""
        self.assertEqual(self.concepts, self.filter_concepts())

    def test_selected_concepts(self):
        """Test that the selected concepts are returned."""
        self.assertEqual({self.bar}, self.filter_concepts(selected_concepts=["bar"]))

    @patch("sys.stderr.write")
    def test_selected_concepts_without_concepts(self, sys_stderr_write: Mock):
        """Test that an empty selection results in an error message."""
        self.assertRaises(SystemExit, self.filter_concepts, selected_concepts=["baz"])
        self.assertIn("Concept 'baz' not found", sys_stderr_write.call_args_list[1][0][0])

    def test_add_hypernyms_and_hyponyms_of_selected_concepts(self):
        """Test that the hypernyms and hyponyms of selected concepts are added."""
        little_bar = create_concept("little bar", dict(hypernym="bar"))
        little_beer_bar = create_concept("little beer bar", dict(hypernym="little bar"))
        self.assertEqual(
            {self.bar, little_bar, little_beer_bar},
            self.filter_concepts(concepts=self.concepts | {little_bar, little_beer_bar}, selected_concepts=["bar"]),
        )

    def test_add_holonyms_and_meronyms_of_selected_concepts(self):
        """Test that the holonyms and meronyms of selected concepts are added."""
        bar_part = create_concept("bar part", dict(holonym="bar"))
        bar_part_part = create_concept("bar part part", dict(holonym="bar part"))
        self.assertEqual(
            {self.bar, bar_part, bar_part_part},
            self.filter_concepts(concepts=self.concepts | {bar_part, bar_part_part}, selected_concepts=["bar"]),
        )

    def test_add_hyponyms_of_meronyms_of_selected_concepts(self):
        """Test that hyponyms of meronyms of selected concepts are added."""
        bar_part = create_concept("bar part", dict(holonym="bar"))
        little_bar_part = create_concept("little bar part", dict(hypernym="bar part"))
        self.assertEqual(
            {self.bar, bar_part, little_bar_part},
            self.filter_concepts(concepts=self.concepts | {bar_part, little_bar_part}, selected_concepts=["bar"]),
        )

    def test_add_meronyms_of_hyponyms_of_selected_concepts(self):
        """Test that meronyms of hyponyms of selected concepts are added."""
        little_bar = create_concept("little bar", dict(hypernym="bar"))
        little_bar_part = create_concept("little bar part", dict(holonym="little bar"))
        self.assertEqual(
            {self.bar, little_bar, little_bar_part},
            self.filter_concepts(concepts=self.concepts | {little_bar, little_bar_part}, selected_concepts=["bar"]),
        )

    def test_add_antonyms_of_selected_concepts(self):
        """Test that antonyms of selected concepts are added."""
        anti_foo = create_concept("anti foo", dict(antonym="foo"))
        self.assertEqual(
            {self.foo, anti_foo},
            self.filter_concepts(concepts=self.concepts | {anti_foo}, selected_concepts=["anti foo"]),
        )

    def test_add_concepts_that_have_selected_concepts_as_root(self):
        """Test that the concepts that have a selected concept as root are added."""
        little_bar = create_concept("little bar", dict(roots="bar"))
        self.assertEqual(
            {self.bar, little_bar},
            self.filter_concepts(concepts=self.concepts | {little_bar}, selected_concepts=["bar"]),
        )

    def test_add_concepts_involved_with_and_by_selected_concepts(self):
        """Test that concepts involved with and by selected concepts are added."""
        zoo = create_concept("zoo", dict(involves="bar"))
        self.assertEqual(
            {self.bar, zoo},
            self.filter_concepts(concepts=self.concepts | {zoo}, selected_concepts=["bar"]),
        )
        self.assertEqual(
            {self.bar, zoo},
            self.filter_concepts(concepts=self.concepts | {zoo}, selected_concepts=["zoo"]),
        )
