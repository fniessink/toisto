"""Unit tests for the model filter."""

from argparse import ArgumentParser
from unittest.mock import Mock, patch

from toisto.model.filter import filter_concepts
from toisto.model.language import EN
from toisto.model.language.concept import Concept

from ...base import ToistoTestCase


class FilterTest(ToistoTestCase):
    """Unit tests for the filter method."""

    def setUp(self) -> None:
        """Set up the unit test fixtures."""
        super().setUp()
        Concept.instances.clear()
        self.argument_parser = ArgumentParser()
        self.foo = self.create_concept("foo", labels=[dict(label="foo", language=EN)])
        self.bar = self.create_concept("bar", labels=[dict(label="bar", language=EN)])
        self.bar_id = self.bar.concept_id
        self.concepts = {self.foo, self.bar}

    def filter_concepts(
        self,
        *,
        concepts: set[Concept] | None = None,
        selected_concepts: list[str] | None = None,
    ) -> set[Concept]:
        """Filter the concepts."""
        return filter_concepts(
            self.concepts if concepts is None else concepts,
            selected_concepts or [],
            EN,
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
    def test_selected_concepts_without_concepts(self, sys_stderr_write: Mock) -> None:
        """Test that an empty selection results in an error message."""
        self.assertRaises(SystemExit, self.filter_concepts, selected_concepts=["baz"])
        self.assertIn("'baz' not found", sys_stderr_write.call_args_list[1][0][0])

    def test_add_hyponyms_of_selected_concepts_recursively(self):
        """Test that the hyponyms of selected concepts are added, recursively."""
        little_bar = self.create_concept("little bar", dict(hypernym=self.bar_id))
        little_beer_bar = self.create_concept("little beer bar", dict(hypernym=little_bar.concept_id))
        self.assertEqual(
            {self.bar, little_bar, little_beer_bar},
            self.filter_concepts(concepts=self.concepts | {little_bar, little_beer_bar}, selected_concepts=["bar"]),
        )

    def test_do_not_add_hypernyms_of_selected_concepts(self):
        """Test that the hypernyms of selected concepts are not added."""
        little_bar = self.create_concept("little bar", dict(hypernym=self.bar_id))
        little_beer_bar = self.create_concept(
            "little beer bar", dict(hypernym=little_bar.concept_id), labels=[dict(label="little beer bar", language=EN)]
        )
        self.assertEqual(
            {little_beer_bar},
            self.filter_concepts(
                concepts=self.concepts | {little_bar, little_beer_bar}, selected_concepts=["little beer bar"]
            ),
        )

    def test_add_meronyms_of_selected_concepts_recursively(self):
        """Test that the holonyms and meronyms of selected concepts are added, recursively."""
        bar_part = self.create_concept("bar part", dict(holonym=self.bar_id))
        bar_part_part = self.create_concept("bar part part", dict(holonym=bar_part.concept_id))
        self.assertEqual(
            {self.bar, bar_part, bar_part_part},
            self.filter_concepts(concepts=self.concepts | {bar_part, bar_part_part}, selected_concepts=["bar"]),
        )

    def test_do_not_add_holonyms_of_selected_concepts(self):
        """Test that the holonyms of selected concepts are not added."""
        bar_part = self.create_concept("bar part", dict(holonym=self.bar_id))
        bar_part_part = self.create_concept(
            "bar part part", dict(holonym=bar_part.concept_id), labels=[dict(label="bar part part", language=EN)]
        )
        self.assertEqual(
            {bar_part_part},
            self.filter_concepts(
                concepts=self.concepts | {bar_part, bar_part_part}, selected_concepts=["bar part part"]
            ),
        )

    def test_add_hyponyms_of_meronyms_of_selected_concepts(self):
        """Test that hyponyms of meronyms of selected concepts are added."""
        bar_part = self.create_concept("bar part", dict(holonym=self.bar_id))
        little_bar_part = self.create_concept("little bar part", dict(hypernym=bar_part.concept_id))
        self.assertEqual(
            {self.bar, bar_part, little_bar_part},
            self.filter_concepts(concepts=self.concepts | {bar_part, little_bar_part}, selected_concepts=["bar"]),
        )

    def test_add_meronyms_of_hyponyms_of_selected_concepts(self):
        """Test that meronyms of hyponyms of selected concepts are added."""
        little_bar = self.create_concept("little bar", dict(hypernym=self.bar_id))
        little_bar_part = self.create_concept("little bar part", dict(holonym=little_bar.concept_id))
        self.assertEqual(
            {self.bar, little_bar, little_bar_part},
            self.filter_concepts(concepts=self.concepts | {little_bar, little_bar_part}, selected_concepts=["bar"]),
        )

    def test_add_antonyms_of_selected_concepts(self):
        """Test that antonyms of selected concepts are added."""
        anti_foo = self.create_concept(
            "anti foo", dict(antonym=self.foo.concept_id), labels=[dict(label="anti foo", language=EN)]
        )
        self.assertEqual(
            {self.foo, anti_foo},
            self.filter_concepts(concepts=self.concepts | {anti_foo}, selected_concepts=["anti foo"]),
        )

    def test_add_concepts_that_have_selected_concepts_as_root(self):
        """Test that the concepts that have a selected concept as root are added."""
        little_bar = self.create_concept("little bar", dict(roots=self.bar_id))
        self.assertEqual(
            {self.bar, little_bar},
            self.filter_concepts(concepts=self.concepts | {little_bar}, selected_concepts=["bar"]),
        )

    def test_add_concepts_involved_by_selected_concepts_recursively(self):
        """Test that concepts involved by selected concepts are added, recursively."""
        zoo = self.create_concept("zoo", dict(involves=self.bar_id))
        baz = self.create_concept("baz", dict(involves=zoo.concept_id), labels=[dict(label="baz", language=EN)])
        self.assertEqual(
            {self.bar, baz, zoo},
            self.filter_concepts(concepts=self.concepts | {baz, zoo}, selected_concepts=["baz"]),
        )
