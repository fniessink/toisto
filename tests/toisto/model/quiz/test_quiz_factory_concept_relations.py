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
        constituent_ids = ("morning/singular", "morning/plural")
        expected_uses = {
            self.create_quiz("morning", "fi", "nl", "Aamu", ["De ochtend"]): (),
            self.create_quiz("morning", "nl", "fi", "De ochtend", ["Aamu"]): (),
            self.create_quiz("morning", "fi", "fi", "Aamu", ["Aamu"], "listen"): (),
            self.create_quiz("morning", "fi", "nl", "Aamut", ["De ochtenden"]): ("morning/singular",),
            self.create_quiz("morning", "nl", "fi", "De ochtenden", ["Aamut"]): ("morning/singular",),
            self.create_quiz("morning", "fi", "fi", "Aamut", ["Aamut"], "listen"): ("morning/singular",),
            self.create_quiz("morning", "fi", "fi", "Aamu", ["Aamut"], "pluralize"): constituent_ids,
            self.create_quiz("morning", "fi", "fi", "Aamut", ["Aamu"], "singularize"): constituent_ids,
        }
        for quiz in self.create_quizzes(concept, "fi", "nl"):
            self.assertEqual(expected_uses[quiz], quiz.uses, msg=quiz)

    def test_generated_uses_for_grammatical_gender(self):
        """Test that use relations are generated for different grammatical genders, i.e. female and male."""
        concept = self.create_noun_with_grammatical_gender()
        constituent_ids = ("cat/female", "cat/male")
        expected_uses = {
            self.create_quiz("cat", "nl", "en", "Haar kat", ["Her cat"], "translate"): (),
            self.create_quiz("cat", "en", "nl", "Her cat", ["Haar kat"], "translate"): (),
            self.create_quiz("cat", "nl", "nl", "Haar kat", ["Haar kat"], "listen"): (),
            self.create_quiz("cat", "nl", "en", "Zijn kat", ["His cat"], "translate"): (),
            self.create_quiz("cat", "en", "nl", "His cat", ["Zijn kat"], "translate"): (),
            self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Zijn kat"], "listen"): (),
            self.create_quiz("cat", "nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"): constituent_ids,
            self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Haar kat"], "feminize"): constituent_ids,
        }
        for quiz in self.create_quizzes(concept, "nl", "en"):
            self.assertEqual(expected_uses[quiz], quiz.uses, msg=quiz)

    def test_generated_uses_for_grammatical_gender_with_neuter(self):
        """Test that use relations are generated for different grammatical genders, i.e. female and male."""
        concept = self.create_noun_with_grammatical_gender_including_neuter()
        constituent_ids = ("bone/female", "bone/male", "bone/neuter")
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
            self.create_quiz("bone", "nl", "nl", "Haar bot", ["Zijn bot"], "masculinize"): constituent_ids,
            self.create_quiz("bone", "nl", "nl", "Haar bot", ["Zijn bot"], "neuterize"): constituent_ids,
            self.create_quiz("bone", "nl", "nl", "Zijn bot", ["Haar bot"], "feminize"): constituent_ids,
        }
        for quiz in self.create_quizzes(concept, "nl", "en"):
            self.assertEqual(expected_uses[quiz], quiz.uses, msg=quiz)

    def test_generated_uses_for_grammatical_number_with_grammatical_gender(self):
        """Test that use relations are generated for grammatical number nested with grammatical gender."""
        concept = self.create_noun_with_grammatical_number_and_gender()
        number_ids = ("cat/singular", "cat/plural")
        singular_gender_ids = ("cat/singular/female", "cat/singular/male")
        plural_gender_ids = ("cat/plural/female", "cat/plural/male")
        expected_uses = {
            self.create_quiz("cat", "nl", "en", "Haar kat", ["Her cat"], "translate"): (),
            self.create_quiz("cat", "en", "nl", "Her cat", ["Haar kat"], "translate"): (),
            self.create_quiz("cat", "nl", "nl", "Haar kat", ["Haar kat"], "listen"): (),
            self.create_quiz("cat", "nl", "en", "Zijn kat", ["His cat"], "translate"): (),
            self.create_quiz("cat", "en", "nl", "His cat", ["Zijn kat"], "translate"): (),
            self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Zijn kat"], "listen"): (),
            self.create_quiz("cat", "nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"): singular_gender_ids,
            self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Haar kat"], "feminize"): singular_gender_ids,
            self.create_quiz("cat", "nl", "en", "Haar katten", ["Her cats"], "translate"): ("cat/singular/female",),
            self.create_quiz("cat", "en", "nl", "Her cats", ["Haar katten"], "translate"): ("cat/singular/female",),
            self.create_quiz("cat", "nl", "nl", "Haar katten", ["Haar katten"], "listen"): ("cat/singular/female",),
            self.create_quiz("cat", "nl", "en", "Zijn katten", ["His cats"], "translate"): ("cat/singular/male",),
            self.create_quiz("cat", "en", "nl", "His cats", ["Zijn katten"], "translate"): ("cat/singular/male",),
            self.create_quiz("cat", "nl", "nl", "Zijn katten", ["Zijn katten"], "listen"): ("cat/singular/male",),
            self.create_quiz("cat", "nl", "nl", "Haar katten", ["Zijn katten"], "masculinize"): plural_gender_ids,
            self.create_quiz("cat", "nl", "nl", "Zijn katten", ["Haar katten"], "feminize"): plural_gender_ids,
            self.create_quiz("cat", "nl", "nl", "Haar kat", ["Haar katten"], "pluralize"): number_ids,
            self.create_quiz("cat", "nl", "nl", "Haar katten", ["Haar kat"], "singularize"): number_ids,
            self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Zijn katten"], "pluralize"): number_ids,
            self.create_quiz("cat", "nl", "nl", "Zijn katten", ["Zijn kat"], "singularize"): number_ids,
        }
        for quiz in self.create_quizzes(concept, "nl", "en"):
            self.assertEqual(expected_uses[quiz], quiz.uses, msg=quiz)

    def test_generated_uses_for_degrees_of_comparison(self):
        """Test that use relations are generated for degrees of comparison."""
        concept = self.create_adjective_with_degrees_of_comparison()
        constituent_ids = ("big/positive degree", "big/comparitive degree", "big/superlative degree")
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
            self.create_quiz("big", "nl", "nl", "Groot", ["Groter"], "give comparitive degree"): constituent_ids,
            self.create_quiz("big", "nl", "nl", "Groot", ["Grootst"], "give superlative degree"): constituent_ids,
            self.create_quiz("big", "nl", "nl", "Groter", ["Groot"], "give positive degree"): constituent_ids,
            self.create_quiz("big", "nl", "nl", "Groter", ["Grootst"], "give superlative degree"): constituent_ids,
            self.create_quiz("big", "nl", "nl", "Grootst", ["Groot"], "give positive degree"): constituent_ids,
            self.create_quiz("big", "nl", "nl", "Grootst", ["Groter"], "give comparitive degree"): constituent_ids,
        }
        for quiz in self.create_quizzes(concept, "nl", "en"):
            self.assertEqual(expected_uses[quiz], quiz.uses, msg=quiz)

    def test_generated_uses_for_tenses(self):
        """Test that use relations are generated for tenses."""
        concept = self.create_verb_with_tense_and_person()
        tense_ids = ("to eat/present tense", "to eat/past tense")
        present_tense_ids = ("to eat/present tense/singular", "to eat/present tense/plural")
        past_tense_ids = ("to eat/past tense/singular", "to eat/past tense/plural")
        expected_uses = {
            self.create_quiz("to eat", "nl", "en", "Ik eet", ["I eat"], "translate"): (),
            self.create_quiz("to eat", "en", "nl", "I eat", ["Ik eet"], "translate"): (),
            self.create_quiz("to eat", "nl", "nl", "Ik eet", ["Ik eet"], "listen"): (),
            self.create_quiz("to eat", "nl", "en", "Wij eten", ["We eat"], "translate"): present_tense_ids[:1],
            self.create_quiz("to eat", "en", "nl", "We eat", ["Wij eten"], "translate"): present_tense_ids[:1],
            self.create_quiz("to eat", "nl", "nl", "Wij eten", ["Wij eten"], "listen"): present_tense_ids[:1],
            self.create_quiz("to eat", "nl", "nl", "Ik eet", ["Wij eten"], "pluralize"): present_tense_ids,
            self.create_quiz("to eat", "nl", "nl", "Wij eten", ["Ik eet"], "singularize"): present_tense_ids,
            self.create_quiz("to eat", "nl", "en", "Ik at", ["I ate"], "translate"): present_tense_ids[:1],
            self.create_quiz("to eat", "en", "nl", "I ate", ["Ik at"], "translate"): present_tense_ids[:1],
            self.create_quiz("to eat", "nl", "nl", "Ik at", ["Ik at"], "listen"): present_tense_ids[:1],
            self.create_quiz("to eat", "nl", "en", "Wij aten", ["We ate"], "translate"): past_tense_ids[:1],
            self.create_quiz("to eat", "en", "nl", "We ate", ["Wij aten"], "translate"): past_tense_ids[:1],
            self.create_quiz("to eat", "nl", "nl", "Wij aten", ["Wij aten"], "listen"): past_tense_ids[:1],
            self.create_quiz("to eat", "nl", "nl", "Ik at", ["Wij aten"], "pluralize"): past_tense_ids,
            self.create_quiz("to eat", "nl", "nl", "Wij aten", ["Ik at"], "singularize"): past_tense_ids,
            self.create_quiz("to eat", "nl", "nl", "Ik eet", ["Ik at"], "give past tense"): tense_ids,
            self.create_quiz("to eat", "nl", "nl", "Wij eten", ["Wij aten"], "give past tense"): tense_ids,
            self.create_quiz("to eat", "nl", "nl", "Ik at", ["Ik eet"], "give present tense"): tense_ids,
            self.create_quiz("to eat", "nl", "nl", "Wij aten", ["Wij eten"], "give present tense"): tense_ids,
        }
        for quiz in self.create_quizzes(concept, "nl", "en"):
            self.assertEqual(expected_uses[quiz], quiz.uses, msg=quiz)
