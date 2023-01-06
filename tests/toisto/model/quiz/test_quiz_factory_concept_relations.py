"""Concept relations unit tests."""

from .test_quiz_factory import QuizFactoryTestCase


class ConceptRelationshipsTest(QuizFactoryTestCase):
    """Unit tests for relationships between concepts."""

    def test_concept_relationship_leaf_concept(self):
        """Test that concepts can declare to use, i.e. depend on, other concepts."""
        concept = self.create_concept(
            "mall",
            dict(uses=["shop", "centre"], fi="Kauppakeskus", nl="Het winkelcentrum"),
        )
        self.assertEqual(("shop", "centre"), self.create_quizzes(concept, "fi", "nl").pop().uses)

    def test_concept_relationship_composite_concept(self):
        """Test that concepts can declare to use, i.e. depend on, other concepts."""
        concept = self.create_concept(
            "mall",
            dict(
                uses=["shop", "centre"],
                singular=dict(fi="Kauppakeskus", nl="Het winkelcentrum"),
                plural=dict(fi="Kauppakeskukset", nl="De winkelcentra"),
            ),
        )
        for quiz in self.create_quizzes(concept, "fi", "nl"):
            self.assertIn("shop", quiz.uses)
            self.assertIn("centre", quiz.uses)

    def test_concept_relationship_leaf_concept_one_uses(self):
        """Test that concepts can declare to use, i.e. depend on, other concepts."""
        concept = self.create_concept("capital", dict(uses="city", fi="Pääkaupunki", en="Capital"))
        self.assertEqual(("city",), self.create_quizzes(concept, "fi", "en").pop().uses)

    def test_generated_concept_ids_for_constituent_concepts(self):
        """Test that constituent concepts get a generated concept id."""
        concept = self.create_noun_with_grammatical_number()
        expected_concept_ids = {
            self.create_quiz("morning", "fi", "nl", "Aamu", ["De ochtend"]): "morning/singular",
            self.create_quiz("morning", "nl", "fi", "De ochtend", ["Aamu"]): "morning/singular",
            self.create_quiz("morning", "fi", "fi", "Aamu", ["Aamu"], "listen"): "morning/singular",
            self.create_quiz("morning", "fi", "nl", "Aamut", ["De ochtenden"]): "morning/plural",
            self.create_quiz("morning", "nl", "fi", "De ochtenden", ["Aamut"]): "morning/plural",
            self.create_quiz("morning", "fi", "fi", "Aamut", ["Aamut"], "listen"): "morning/plural",
            self.create_quiz("morning", "fi", "fi", "Aamu", ["Aamut"], "pluralize"): "morning",
            self.create_quiz("morning", "fi", "fi", "Aamut", ["Aamu"], "singularize"): "morning",
        }
        for quiz in self.create_quizzes(concept, "fi", "nl"):
            self.assertEqual(expected_concept_ids[quiz], quiz.concept_id)

    def test_generated_uses_for_grammatical_number(self):
        """Test that constituent concepts get a generated uses list."""
        concept = self.create_noun_with_grammatical_number()
        expected_uses = {
            self.create_quiz("morning", "fi", "nl", "Aamu", ["De ochtend"]): (),
            self.create_quiz("morning", "nl", "fi", "De ochtend", ["Aamu"]): (),
            self.create_quiz("morning", "fi", "fi", "Aamu", ["Aamu"], "listen"): (),
            self.create_quiz("morning", "fi", "nl", "Aamut", ["De ochtenden"]): ("morning/singular",),
            self.create_quiz("morning", "nl", "fi", "De ochtenden", ["Aamut"]): ("morning/singular",),
            self.create_quiz("morning", "fi", "fi", "Aamut", ["Aamut"], "listen"): ("morning/singular",),
            self.create_quiz("morning", "fi", "fi", "Aamu", ["Aamut"], "pluralize"): (
                "morning/singular",
                "morning/plural",
            ),
            self.create_quiz("morning", "fi", "fi", "Aamut", ["Aamu"], "singularize"): (
                "morning/plural",
                "morning/singular",
            ),
        }
        for quiz in self.create_quizzes(concept, "fi", "nl"):
            self.assertEqual(expected_uses[quiz], quiz.uses)

    def test_generated_uses_for_grammatical_gender(self):
        """Test that use relations are generated for different grammatical genders, i.e. female and male."""
        concept = self.create_noun_with_grammatical_gender()
        expected_uses = {
            self.create_quiz("cat", "nl", "en", "Haar kat", ["Her cat"], "translate"): (),
            self.create_quiz("cat", "en", "nl", "Her cat", ["Haar kat"], "translate"): (),
            self.create_quiz("cat", "nl", "nl", "Haar kat", ["Haar kat"], "listen"): (),
            self.create_quiz("cat", "nl", "en", "Zijn kat", ["His cat"], "translate"): (),
            self.create_quiz("cat", "en", "nl", "His cat", ["Zijn kat"], "translate"): (),
            self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Zijn kat"], "listen"): (),
            self.create_quiz("cat", "nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"): ("cat/female", "cat/male"),
            self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Haar kat"], "feminize"): ("cat/male", "cat/female"),
        }
        for quiz in self.create_quizzes(concept, "nl", "en"):
            self.assertEqual(expected_uses[quiz], quiz.uses)

    def test_generated_uses_for_grammatical_gender_with_neuter(self):
        """Test that use relations are generated for different grammatical genders, i.e. female and male."""
        concept = self.create_noun_with_grammatical_gender_including_neuter()
        expected_uses = {
            self.create_quiz("bone", "nl", "en", "Haar bot", ["Her bone"], "translate"): (),
            self.create_quiz("bone", "en", "nl", "Her bone", ["Haar bot"], "translate"): (),
            self.create_quiz("bone", "nl", "nl", "Haar bot", ["Haar bot"], "listen"): (),
            self.create_quiz("bone", "nl", "en", "Zijn bot", ["His bone"], "translate"): (),
            self.create_quiz("bone", "en", "nl", "His bone", ["Zijn bot"], "translate"): (),
            self.create_quiz("bone", "nl", "nl", "Zijn bot", ["Zijn bot"], "listen"): (),
            self.create_quiz("bone", "nl", "en", "Zijn bot", ["Its bone"], "translate"): (),
            self.create_quiz("bone", "en", "nl", "Its bone", ["Zijn bot"], "translate"): (),
            self.create_quiz("bone", "nl", "nl", "Zijn bot", ["Zijn bot"], "listen"): (),
            self.create_quiz("bone", "nl", "nl", "Haar bot", ["Zijn bot"], "masculinize"): ("bone/female", "bone/male"),
            self.create_quiz("bone", "nl", "nl", "Haar bot", ["Zijn bot"], "neuterize"): ("bone/female", "bone/neuter"),
            self.create_quiz("bone", "nl", "nl", "Zijn bot", ["Haar bot"], "feminize"): ("bone/neuter", "bone/female"),
            self.create_quiz("bone", "nl", "nl", "Zijn bot", ["Haar bot"], "feminize"): ("bone/male", "bone/female"),
        }
        for quiz in self.create_quizzes(concept, "nl", "en"):
            self.assertEqual(expected_uses[quiz], quiz.uses)

    def test_generated_uses_for_grammatical_number_with_grammatical_gender(self):
        """Test that use relations are generated for grammatical number nested with grammatical gender."""
        concept = self.create_noun_with_grammatical_number_and_gender()
        expected_uses = {
            self.create_quiz("cat", "nl", "en", "Haar kat", ["Her cat"], "translate"): (),
            self.create_quiz("cat", "en", "nl", "Her cat", ["Haar kat"], "translate"): (),
            self.create_quiz("cat", "nl", "nl", "Haar kat", ["Haar kat"], "listen"): (),
            self.create_quiz("cat", "nl", "en", "Zijn kat", ["His cat"], "translate"): (),
            self.create_quiz("cat", "en", "nl", "His cat", ["Zijn kat"], "translate"): (),
            self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Zijn kat"], "listen"): (),
            self.create_quiz("cat", "nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"): (
                "cat/singular/female",
                "cat/singular/male",
            ),
            self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Haar kat"], "feminize"): (
                "cat/singular/male",
                "cat/singular/female",
            ),
            self.create_quiz("cat", "nl", "en", "Haar katten", ["Her cats"], "translate"): ("cat/singular/female",),
            self.create_quiz("cat", "en", "nl", "Her cats", ["Haar katten"], "translate"): ("cat/singular/female",),
            self.create_quiz("cat", "nl", "nl", "Haar katten", ["Haar katten"], "listen"): ("cat/singular/female",),
            self.create_quiz("cat", "nl", "en", "Zijn katten", ["His cats"], "translate"): ("cat/singular/male",),
            self.create_quiz("cat", "en", "nl", "His cats", ["Zijn katten"], "translate"): ("cat/singular/male",),
            self.create_quiz("cat", "nl", "nl", "Zijn katten", ["Zijn katten"], "listen"): ("cat/singular/male",),
            self.create_quiz("cat", "nl", "nl", "Haar katten", ["Zijn katten"], "masculinize"): (
                "cat/plural/female",
                "cat/plural/male",
            ),
            self.create_quiz("cat", "nl", "nl", "Zijn katten", ["Haar katten"], "feminize"): (
                "cat/plural/male",
                "cat/plural/female",
            ),
            self.create_quiz("cat", "nl", "nl", "Haar kat", ["Haar katten"], "pluralize"): (
                "cat/singular/female",
                "cat/plural/female",
            ),
            self.create_quiz("cat", "nl", "nl", "Haar katten", ["Haar kat"], "singularize"): (
                "cat/plural/female",
                "cat/singular/female",
            ),
            self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Zijn katten"], "pluralize"): (
                "cat/singular/male",
                "cat/plural/male",
            ),
            self.create_quiz("cat", "nl", "nl", "Zijn katten", ["Zijn kat"], "singularize"): (
                "cat/plural/male",
                "cat/singular/male",
            ),
        }
        for quiz in self.create_quizzes(concept, "nl", "en"):
            self.assertEqual(expected_uses[quiz], quiz.uses)

    def test_generated_uses_for_degrees_of_comparison(self):
        """Test that use relations are generated for degrees of comparison."""
        concept = self.create_adjective_with_degrees_of_comparison()
        expected_uses = {
            self.create_quiz("big", "nl", "en", "Groot", ["Big"], "translate"): (),
            self.create_quiz("big", "en", "nl", "Big", ["Groot"], "translate"): (),
            self.create_quiz("big", "nl", "nl", "Groot", ["Groot"], "listen"): (),
            self.create_quiz("big", "nl", "en", "Groter", ["Bigger"], "translate"): (),
            self.create_quiz("big", "en", "nl", "Bigger", ["Groter"], "translate"): (),
            self.create_quiz("big", "nl", "nl", "Groter", ["Groter"], "listen"): (),
            self.create_quiz("big", "nl", "en", "Grootst", ["Biggest"], "translate"): (),
            self.create_quiz("big", "en", "nl", "Biggest", ["Grootst"], "translate"): (),
            self.create_quiz("big", "nl", "nl", "Grootst", ["Grootst"], "listen"): (),
            self.create_quiz("big", "nl", "nl", "Groot", ["Groter"], "give comparitive degree"): (
                "big/positive degree",
                "big/comparitive degree",
            ),
            self.create_quiz("big", "nl", "nl", "Groot", ["Grootst"], "give superlative degree"): (
                "big/positive degree",
                "big/superlative degree",
            ),
            self.create_quiz("big", "nl", "nl", "Groter", ["Groot"], "give positive degree"): (
                "big/comparitive degree",
                "big/positive degree",
            ),
            self.create_quiz("big", "nl", "nl", "Groter", ["Grootst"], "give superlative degree"): (
                "big/comparitive degree",
                "big/superlative degree",
            ),
            self.create_quiz("big", "nl", "nl", "Grootst", ["Groot"], "give positive degree"): (
                "big/superlative degree",
                "big/positive degree",
            ),
            self.create_quiz("big", "nl", "nl", "Grootst", ["Groter"], "give comparitive degree"): (
                "big/superlative degree",
                "big/comparitive degree",
            ),
        }
        for quiz in self.create_quizzes(concept, "nl", "en"):
            self.assertEqual(expected_uses[quiz], quiz.uses)

    def test_generated_uses_for_tenses(self):
        """Test that use relations are generated for tenses."""
        concept = self.create_verb_with_tense_and_person()
        expected_uses = {
            self.create_quiz("to eat", "nl", "en", "Ik eet", ["I eat"], "translate"): (),
            self.create_quiz("to eat", "en", "nl", "I eat", ["Ik eet"], "translate"): (),
            self.create_quiz("to eat", "nl", "nl", "Ik eet", ["Ik eet"], "listen"): (),
            self.create_quiz("to eat", "nl", "en", "Wij eten", ["We eat"], "translate"): (
                "to eat/present tense/singular",
            ),
            self.create_quiz("to eat", "en", "nl", "We eat", ["Wij eten"], "translate"): (
                "to eat/present tense/singular",
            ),
            self.create_quiz("to eat", "nl", "nl", "Wij eten", ["Wij eten"], "listen"): (
                "to eat/present tense/singular",
            ),
            self.create_quiz("to eat", "nl", "nl", "Ik eet", ["Wij eten"], "pluralize"): (
                "to eat/present tense/singular",
                "to eat/present tense/plural",
            ),
            self.create_quiz("to eat", "nl", "nl", "Wij eten", ["Ik eet"], "singularize"): (
                "to eat/present tense/plural",
                "to eat/present tense/singular",
            ),
            self.create_quiz("to eat", "nl", "en", "Ik at", ["I ate"], "translate"): ("to eat/present tense/singular",),
            self.create_quiz("to eat", "en", "nl", "I ate", ["Ik at"], "translate"): ("to eat/present tense/singular",),
            self.create_quiz("to eat", "nl", "nl", "Ik at", ["Ik at"], "listen"): ("to eat/present tense/singular",),
            self.create_quiz("to eat", "nl", "en", "Wij aten", ["We ate"], "translate"): (
                "to eat/past tense/singular",
            ),
            self.create_quiz("to eat", "en", "nl", "We ate", ["Wij aten"], "translate"): (
                "to eat/past tense/singular",
            ),
            self.create_quiz("to eat", "nl", "nl", "Wij aten", ["Wij aten"], "listen"): ("to eat/past tense/singular",),
            self.create_quiz("to eat", "nl", "nl", "Ik at", ["Wij aten"], "pluralize"): (
                "to eat/past tense/singular",
                "to eat/past tense/plural",
            ),
            self.create_quiz("to eat", "nl", "nl", "Wij aten", ["Ik at"], "singularize"): (
                "to eat/past tense/plural",
                "to eat/past tense/singular",
            ),
            self.create_quiz("to eat", "nl", "nl", "Ik eet", ["Ik at"], "give past tense"): (
                "to eat/present tense/singular",
                "to eat/past tense/singular",
            ),
            self.create_quiz("to eat", "nl", "nl", "Wij eten", ["Wij aten"], "give past tense"): (
                "to eat/present tense/plural",
                "to eat/past tense/plural",
            ),
            self.create_quiz("to eat", "nl", "nl", "Ik at", ["Ik eet"], "give present tense"): (
                "to eat/past tense/singular",
                "to eat/present tense/singular",
            ),
            self.create_quiz("to eat", "nl", "nl", "Wij aten", ["Wij eten"], "give present tense"): (
                "to eat/past tense/plural",
                "to eat/present tense/plural",
            ),
        }
        for quiz in self.create_quizzes(concept, "nl", "en"):
            self.assertEqual(expected_uses[quiz], quiz.uses, msg=quiz)
