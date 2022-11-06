"""Concept unit tests."""

from toisto.model import concept_factory, Label

from ..base import ToistoTestCase


class ConceptTest(ToistoTestCase):
    """Unit tests for the concept class."""

    def test_quizzes(self):
        """Test that quizzes can be generated from a concept."""
        concept = concept_factory(dict(en=["English"], nl=["Engels"]))
        self.assertEqual(
            [
                self.create_quiz("nl", "en", "Engels", ["English"]),
                self.create_quiz("en", "nl", "English", ["Engels"])
            ],
            concept.quizzes("nl", "en")
        )

    def test_multiple_labels(self):
        """Test that quizzes can be generated from a concept with a language with multiple labels."""
        concept = concept_factory(dict(nl=["Bank"], en=["Couch", "Bank"]))
        self.assertEqual(
            [
                self.create_quiz("nl", "en", "Bank", ["Couch", "Bank"]),
                self.create_quiz("en", "nl", "Couch", ["Bank"]),
                self.create_quiz("en", "nl", "Bank", ["Bank"])
            ],
            concept.quizzes("nl", "en")
        )

    def test_missing_language(self):
        """Test that quizzes can be generated from a concept even if it's missing one of the languages."""
        concept = concept_factory(dict(en=["English"], nl=["Engels"]))
        self.assertEqual([], concept.quizzes("fi", "en"))

    def test_grammatical_number(self):
        """Test that quizzes can be generated for different grammatical numbers, i.e. singular and plural."""
        concept = concept_factory(
            dict(singular=dict(fi="Aamu", nl="De ochtend"), plural=dict(fi="Aamut", nl="De ochtenden"))
        )
        self.assertEqual(
            [
                self.create_quiz("fi", "nl", "Aamu", ["De ochtend"]),
                self.create_quiz("nl", "fi", "De ochtend", ["Aamu"]),
                self.create_quiz("fi", "nl", "Aamut", ["De ochtenden"]),
                self.create_quiz("nl", "fi", "De ochtenden", ["Aamut"]),
                self.create_quiz("fi", "fi", "Aamu", ["Aamut"], "pluralize"),
                self.create_quiz("fi", "fi", "Aamut", ["Aamu"], "singularize")
            ],
            concept.quizzes("fi", "nl")
        )

    def test_grammatical_number_without_plural(self):
        """Test that quizzes can be generated even if one language has no plural labels for the concept."""
        concept = concept_factory(dict(singular=dict(fi="Ketsuppi", nl="De ketchup"), plural=dict(fi="Ketsupit")))
        self.assertEqual(
            [
                self.create_quiz("fi", "nl", "Ketsuppi", ["De ketchup"]),
                self.create_quiz("nl", "fi", "De ketchup", ["Ketsuppi"]),
                self.create_quiz("fi", "fi", "Ketsuppi", ["Ketsupit"], "pluralize"),
                self.create_quiz("fi", "fi", "Ketsupit", ["Ketsuppi"], "singularize")
            ],
            concept.quizzes("fi", "nl")
        )

    def test_grammatical_number_with_one_language(self):
        """Test that quizzes can be generated from a concept with labels in the practice language only."""
        concept = concept_factory(dict(singular=dict(fi="Mämmi"), plural=dict(fi="Mämmit")))
        self.assertEqual(
            [
                self.create_quiz("fi", "fi", "Mämmi", ["Mämmit"], "pluralize"),
                self.create_quiz("fi", "fi", "Mämmit", ["Mämmi"], "singularize")
            ],
            concept.quizzes("fi", "en")
        )

    def test_grammatical_number_with_one_language_reversed(self):
        """Test that no quizzes can be generated from a noun concept with labels in the native language."""
        concept = concept_factory(dict(singular=dict(fi="Mämmi"), plural=dict(fi="Mämmit")))
        self.assertEqual([], concept.quizzes("en", "fi"))

    def test_grammatical_number_with_synonyms(self):
        """Test that in case of synonyms the plural of one synonym isn't the correct answer for the other synonym."""
        concept = concept_factory(
            dict(
                singular=dict(fi=["Kauppakeskus", "Ostoskeskus"], nl="Het winkelcentrum"),
                plural=dict(fi=["Kauppakeskukset", "Ostoskeskukset"], nl="De winkelcentra")
            )
        )
        self.assertEqual(
            [
                self.create_quiz("fi", "nl", "Kauppakeskus", ["Het winkelcentrum"]),
                self.create_quiz("fi", "nl", "Ostoskeskus", ["Het winkelcentrum"],),
                self.create_quiz("nl", "fi", "Het winkelcentrum", ["Kauppakeskus", "Ostoskeskus"]),
                self.create_quiz("fi", "nl", "Kauppakeskukset", ["De winkelcentra"]),
                self.create_quiz("fi", "nl", "Ostoskeskukset", ["De winkelcentra"]),
                self.create_quiz("nl", "fi", "De winkelcentra", ["Kauppakeskukset", "Ostoskeskukset"]),
                self.create_quiz("fi", "fi", "Kauppakeskus", ["Kauppakeskukset"], "pluralize"),
                self.create_quiz("fi", "fi", "Ostoskeskus", ["Ostoskeskukset"], "pluralize"),
                self.create_quiz("fi", "fi", "Kauppakeskukset", ['Kauppakeskus'], "singularize"),
                self.create_quiz("fi", "fi", "Ostoskeskukset", ["Ostoskeskus"], "singularize")
            ],
            concept.quizzes("fi", "nl")
        )

    def test_grammatical_gender(self):
        """Test that quizzes can be generated for different grammatical genders, i.e. female and male."""
        concept = concept_factory(
            dict(female=dict(en="Her cat", nl="Haar kat"), male=dict(en="His cat", nl="Zijn kat"))
        )
        self.assertEqual(
            [
                self.create_quiz("nl", "en", "Haar kat", ["Her cat"], "translate"),
                self.create_quiz("en", "nl", "Her cat", ["Haar kat"], "translate"),
                self.create_quiz("nl", "en", "Zijn kat", ["His cat"], "translate"),
                self.create_quiz("en", "nl", "His cat", ["Zijn kat"], "translate"),
                self.create_quiz("nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"),
                self.create_quiz("nl", "nl", "Zijn kat", ["Haar kat"], "feminize")
            ],
            concept.quizzes("nl", "en")
        )

    def test_grammatical_gender_with_neuter(self):
        """Test that quizzes can be generated for different grammatical genders, i.e. female and male."""
        concept = concept_factory(
            dict(
                female=dict(en="Her bone", nl="Haar bot"),
                male=dict(en="His bone", nl="Zijn bot"),
                neuter=dict(en="Its bone", nl="Zijn bot")
            )
        )
        self.assertEqual(
            [
                self.create_quiz("nl", "en", "Haar bot", ["Her bone"], "translate"),
                self.create_quiz("en", "nl", "Her bone", ["Haar bot"], "translate"),
                self.create_quiz("nl", "en", "Zijn bot", ["His bone"], "translate"),
                self.create_quiz("en", "nl", "His bone", ["Zijn bot"], "translate"),
                self.create_quiz("nl", "en", "Zijn bot", ["Its bone"], "translate"),
                self.create_quiz("en", "nl", "Its bone", ["Zijn bot"], "translate"),
                self.create_quiz("nl", "nl", "Haar bot", ["Zijn bot"], "masculinize"),
                self.create_quiz("nl", "nl", "Haar bot", ["Zijn bot"], "neuterize"),
                self.create_quiz("nl", "nl", "Zijn bot", ["Haar bot"], "feminize"),
                self.create_quiz("nl", "nl", "Zijn bot", ["Haar bot"], "feminize")
            ],
            concept.quizzes("nl", "en")
        )

    def test_grammatical_number_with_grammatical_gender(self):
        """Test that quizzes can be generated for grammatical number nested with grammatical gender."""
        concept = concept_factory(
            dict(
                singular=dict(female=dict(en="Her cat", nl="Haar kat"), male=dict(en="His cat", nl="Zijn kat")),
                plural=dict(female=dict(en="Her cats", nl="Haar katten"), male=dict(en="His cats", nl="Zijn katten"))
            )
        )
        self.assertEqual(
            [
                self.create_quiz("nl", "en", "Haar kat", ["Her cat"], "translate"),
                self.create_quiz("en", "nl", "Her cat", ["Haar kat"], "translate"),
                self.create_quiz("nl", "en", "Zijn kat", ["His cat"], "translate"),
                self.create_quiz("en", "nl", "His cat", ["Zijn kat"], "translate"),
                self.create_quiz("nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"),
                self.create_quiz("nl", "nl", "Zijn kat", ["Haar kat"], "feminize"),
                self.create_quiz("nl", "en", "Haar katten", ["Her cats"], "translate"),
                self.create_quiz("en", "nl", "Her cats", ["Haar katten"], "translate"),
                self.create_quiz("nl", "en", "Zijn katten", ["His cats"], "translate"),
                self.create_quiz("en", "nl", "His cats", ["Zijn katten"], "translate"),
                self.create_quiz("nl", "nl", "Haar katten", ["Zijn katten"], "masculinize"),
                self.create_quiz("nl", "nl", "Zijn katten", ["Haar katten"], "feminize"),
                self.create_quiz("nl", "nl", "Haar kat", ["Haar katten"], "pluralize"),
                self.create_quiz("nl", "nl", "Haar katten", ["Haar kat"], "singularize"),
                self.create_quiz("nl", "nl", "Zijn kat", ["Zijn katten"], "pluralize"),
                self.create_quiz("nl", "nl", "Zijn katten", ["Zijn kat"], "singularize")
            ],
            concept.quizzes("nl", "en")
        )

    def test_degrees_of_comparison(self):
        """Test that quizzes can be generated for degrees of comparison."""
        concept = concept_factory(
            dict(
                positive_degree=dict(en="Big", nl="Groot"),
                comparitive_degree=dict(en="Bigger", nl="Groter"),
                superlative_degree=dict(en="Biggest", nl="Grootst")
            )
        )
        self.assertEqual(
            [
                self.create_quiz("nl", "en", "Groot", ["Big"], "translate"),
                self.create_quiz("en", "nl", "Big", ["Groot"], "translate"),
                self.create_quiz("nl", "en", "Groter", ["Bigger"], "translate"),
                self.create_quiz("en", "nl", "Bigger", ["Groter"], "translate"),
                self.create_quiz("nl", "en", "Grootst", ["Biggest"], "translate"),
                self.create_quiz("en", "nl", "Biggest", ["Grootst"], "translate"),
                self.create_quiz("nl", "nl", "Groot", ["Groter"], "give comparitive degree"),
                self.create_quiz("nl", "nl", "Groot", ["Grootst"], "give superlative degree"),
                self.create_quiz("nl", "nl", "Groter", ["Groot"], "give positive degree"),
                self.create_quiz("nl", "nl", "Groter", ["Grootst"], "give superlative degree"),
                self.create_quiz("nl", "nl", "Grootst", ["Groot"], "give positive degree"),
                self.create_quiz("nl", "nl", "Grootst", ["Groter"], "give comparitive degree"),
            ],
            concept.quizzes("nl", "en")
        )

    def test_degrees_of_comparison_with_synonyms(self):
        """Test that quizzes can be generated for degrees of comparison with synonyms."""
        concept = concept_factory(
            dict(
                positive_degree=dict(en="Big", fi=["Iso", "Suuri"]),
                comparitive_degree=dict(en="Bigger", fi=["Isompi", "Suurempi"]),
                superlative_degree=dict(en="Biggest", fi=["Isoin", "Suurin"])
            )
        )
        self.assertEqual(
            [
                self.create_quiz("fi", "en", "Iso", ["Big"], "translate"),
                self.create_quiz("fi", "en", "Suuri", ["Big"], "translate"),
                self.create_quiz("en", "fi", "Big", ["Iso", "Suuri"], "translate"),
                self.create_quiz("fi", "en", "Isompi", ["Bigger"], "translate"),
                self.create_quiz("fi", "en", "Suurempi", ["Bigger"], "translate"),
                self.create_quiz("en", "fi", "Bigger", ["Isompi", "Suurempi"], "translate"),
                self.create_quiz("fi", "en", "Isoin", ["Biggest"], "translate"),
                self.create_quiz("fi", "en", "Suurin", ["Biggest"], "translate"),
                self.create_quiz("en", "fi", "Biggest", ["Isoin", "Suurin"], "translate"),
                self.create_quiz("fi", "fi", "Iso", ["Isompi"], "give comparitive degree"),
                self.create_quiz("fi", "fi", "Suuri", ["Suurempi"], "give comparitive degree"),
                self.create_quiz("fi", "fi", "Iso", ["Isoin"], "give superlative degree"),
                self.create_quiz("fi", "fi", "Suuri", ["Suurin"], "give superlative degree"),
                self.create_quiz("fi", "fi", "Isompi", ["Iso"], "give positive degree"),
                self.create_quiz("fi", "fi", "Suurempi", ["Suuri"], "give positive degree"),
                self.create_quiz("fi", "fi", "Isompi", ["Isoin"], "give superlative degree"),
                self.create_quiz("fi", "fi", "Suurempi", ["Suurin"], "give superlative degree"),
                self.create_quiz("fi", "fi", "Isoin", ["Iso"], "give positive degree"),
                self.create_quiz("fi", "fi", "Suurin", ["Suuri"], "give positive degree"),
                self.create_quiz("fi", "fi", "Isoin", ["Isompi"], "give comparitive degree"),
                self.create_quiz("fi", "fi", "Suurin", ["Suurempi"], "give comparitive degree"),
            ],
            concept.quizzes("fi", "en")
        )

    def test_grammatical_person(self):
        """Test that quizzes can be generated for grammatical person."""
        concept = concept_factory(
            dict(
                first_person=dict(en="I eat", nl="Ik eet"),
                second_person=dict(en="You eat", nl="Jij eet"),
                third_person=dict(en="She eats", nl="Zij eet")
            )
        )
        self.assertEqual(
            [
                self.create_quiz("nl", "en", "Ik eet", ["I eat"], "translate"),
                self.create_quiz("en", "nl", "I eat", ["Ik eet"], "translate"),
                self.create_quiz("nl", "en", "Jij eet", ["You eat"], "translate"),
                self.create_quiz("en", "nl", "You eat", ["Jij eet"], "translate"),
                self.create_quiz("nl", "en", "Zij eet", ["She eats"], "translate"),
                self.create_quiz("en", "nl", "She eats", ["Zij eet"], "translate"),
                self.create_quiz("nl", "nl", "Ik eet", ["Jij eet"], "give second person"),
                self.create_quiz("nl", "nl", "Ik eet", ["Zij eet"], "give third person"),
                self.create_quiz("nl", "nl", "Jij eet", ["Ik eet"], "give first person"),
                self.create_quiz("nl", "nl", "Jij eet", ["Zij eet"], "give third person"),
                self.create_quiz("nl", "nl", "Zij eet", ["Ik eet"], "give first person"),
                self.create_quiz("nl", "nl", "Zij eet", ["Jij eet"], "give second person"),
            ],
            concept.quizzes("nl", "en")
        )

    def test_grammatical_person_nested_with_grammatical_gender(self):
        """Test that quizzes can be generated for grammatical person, nested with grammatical gender."""
        concept = concept_factory(
            dict(
                first_person=dict(en="I eat", nl="Ik eet"),
                second_person=dict(en="You eat", nl="Jij eet"),
                third_person=dict(female=dict(en="She eats", nl="Zij eet"), male=dict(en="He eats", nl="Hij eet"))
            )
        )
        self.assertEqual(
            [
                self.create_quiz("nl", "en", "Ik eet", ["I eat"], "translate"),
                self.create_quiz("en", "nl", "I eat", ["Ik eet"], "translate"),
                self.create_quiz("nl", "en", "Jij eet", ["You eat"], "translate"),
                self.create_quiz("en", "nl", "You eat", ["Jij eet"], "translate"),
                self.create_quiz("nl", "en", "Zij eet", ["She eats"], "translate"),
                self.create_quiz("en", "nl", "She eats", ["Zij eet"], "translate"),
                self.create_quiz("nl", "en", "Hij eet", ["He eats"], "translate"),
                self.create_quiz("en", "nl", "He eats", ["Hij eet"], "translate"),
                self.create_quiz("nl", "nl", "Zij eet", ["Hij eet"], "masculinize"),
                self.create_quiz("nl", "nl", "Hij eet", ["Zij eet"], "feminize"),
                self.create_quiz("nl", "nl", "Ik eet", ["Jij eet"], "give second person"),
                self.create_quiz("nl", "nl", "Ik eet", ["Zij eet"], "give third person"),
                self.create_quiz("nl", "nl", "Jij eet", ["Ik eet"], "give first person"),
                self.create_quiz("nl", "nl", "Jij eet", ["Zij eet"], "give third person"),
                self.create_quiz("nl", "nl", "Zij eet", ["Ik eet"], "give first person"),
                self.create_quiz("nl", "nl", "Zij eet", ["Jij eet"], "give second person"),
            ],
            concept.quizzes("nl", "en")
        )

    def test_grammatical_number_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for grammatical number, nested with grammatical person."""
        concept = concept_factory(
            dict(
                singular=dict(
                    first_person=dict(fi="Minulla on", nl="Ik heb"),
                    second_person=dict(fi="Sinulla on", nl="Jij hebt"),
                    third_person=dict(fi="Hänellä on", nl="Zij heeft"),
                ),
                plural=dict(
                    first_person=dict(fi="Meillä on", nl="Wij hebben"),
                    second_person=dict(fi="Teillä on", nl="Jullie hebben"),
                    third_person=dict(fi="Heillä on", nl="Zij hebben"),
                )
            )
        )
        self.assertEqual(
            [
                self.create_quiz("nl", "fi", "Ik heb", ["Minulla on"], "translate"),
                self.create_quiz("fi", "nl", "Minulla on", ["Ik heb"], "translate"),
                self.create_quiz("nl", "fi", "Jij hebt", ["Sinulla on"], "translate"),
                self.create_quiz("fi", "nl", "Sinulla on", ["Jij hebt"], "translate"),
                self.create_quiz("nl", "fi", "Zij heeft", ["Hänellä on"], "translate"),
                self.create_quiz("fi", "nl", "Hänellä on", ["Zij heeft"], "translate"),
                self.create_quiz("nl", "nl", "Ik heb", ["Jij hebt"], "give second person"),
                self.create_quiz("nl", "nl", "Ik heb", ["Zij heeft"], "give third person"),
                self.create_quiz("nl", "nl", "Jij hebt", ["Ik heb"], "give first person"),
                self.create_quiz("nl", "nl", "Jij hebt", ["Zij heeft"], "give third person"),
                self.create_quiz("nl", "nl", "Zij heeft", ["Ik heb"], "give first person"),
                self.create_quiz("nl", "nl", "Zij heeft", ["Jij hebt"], "give second person"),
                self.create_quiz("nl", "fi", "Wij hebben", ["Meillä on"], "translate"),
                self.create_quiz("fi", "nl", "Meillä on", ["Wij hebben"], "translate"),
                self.create_quiz("nl", "fi", "Jullie hebben", ["Teillä on"], "translate"),
                self.create_quiz("fi", "nl", "Teillä on", ["Jullie hebben"], "translate"),
                self.create_quiz("nl", "fi", "Zij hebben", ["Heillä on"], "translate"),
                self.create_quiz("fi", "nl", "Heillä on", ["Zij hebben"], "translate"),
                self.create_quiz("nl", "nl", "Wij hebben", ["Jullie hebben"], "give second person"),
                self.create_quiz("nl", "nl", "Wij hebben", ["Zij hebben"], "give third person"),
                self.create_quiz("nl", "nl", "Jullie hebben", ["Wij hebben"], "give first person"),
                self.create_quiz("nl", "nl", "Jullie hebben", ["Zij hebben"], "give third person"),
                self.create_quiz("nl", "nl", "Zij hebben", ["Wij hebben"], "give first person"),
                self.create_quiz("nl", "nl", "Zij hebben", ["Jullie hebben"], "give second person"),
                self.create_quiz("nl", "nl", "Ik heb", ["Wij hebben"], "pluralize"),
                self.create_quiz("nl", "nl", "Wij hebben", ["Ik heb"], "singularize"),
                self.create_quiz("nl", "nl", "Jij hebt", ["Jullie hebben"], "pluralize"),
                self.create_quiz("nl", "nl", "Jullie hebben", ["Jij hebt"], "singularize"),
                self.create_quiz("nl", "nl", "Zij heeft", ["Zij hebben"], "pluralize"),
                self.create_quiz("nl", "nl", "Zij hebben", ["Zij heeft"], "singularize"),
            ],
            concept.quizzes("nl", "fi")
        )

    def test_grammatical_gender_nested_with_grammatical_number(self):
        """Test that quizzes can be generated for nested concepts."""
        concept = concept_factory(
            dict(
                female=dict(singular=dict(en="Her cat", nl="Haar kat"), plural=dict(en="Her cats", nl="Haar katten")),
                male=dict(singular=dict(en="His cat", nl="Zijn kat"), plural=dict(en="His cats", nl="Zijn katten"))
            )
        )
        self.assertEqual(
            [
                self.create_quiz("nl", "en", "Haar kat", ["Her cat"], "translate"),
                self.create_quiz("en", "nl", "Her cat", ["Haar kat"], "translate"),
                self.create_quiz("nl", "en", "Haar katten", ["Her cats"], "translate"),
                self.create_quiz("en", "nl", "Her cats", ["Haar katten"], "translate"),
                self.create_quiz("nl", "nl", "Haar kat", ["Haar katten"], "pluralize"),
                self.create_quiz("nl", "nl", "Haar katten", ["Haar kat"], "singularize"),
                self.create_quiz("nl", "en", "Zijn kat", ["His cat"], "translate"),
                self.create_quiz("en", "nl", "His cat", ["Zijn kat"], "translate"),
                self.create_quiz("nl", "en", "Zijn katten", ["His cats"], "translate"),
                self.create_quiz("en", "nl", "His cats", ["Zijn katten"], "translate"),
                self.create_quiz("nl", "nl", "Zijn kat", ["Zijn katten"], "pluralize"),
                self.create_quiz("nl", "nl", "Zijn katten", ["Zijn kat"], "singularize"),
                self.create_quiz("nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"),
                self.create_quiz("nl", "nl", "Zijn kat", ["Haar kat"], "feminize"),
                self.create_quiz("nl", "nl", "Haar katten", ["Zijn katten"], "masculinize"),
                self.create_quiz("nl", "nl", "Zijn katten", ["Haar katten"], "feminize")
            ],
            concept.quizzes("nl", "en")
        )

    def test_same_label_in_different_composite_concepts(self):
        """Test that the same label in different leaf concepts is ignored."""
        concept = concept_factory(
            dict(
                female=dict(en="She is|She's", fi="Hän on|On;female"),
                male=dict(en="He is|He's", fi="Hän on|On;male")
            )
        )
        self.assertEqual(
            [
                self.create_quiz("fi", "en", Label("Hän on|On;female"), ["She is|She's"]),
                self.create_quiz("en", "fi", "She is|She's", ["Hän on|On;female"]),
                self.create_quiz("fi", "en", "Hän on|On;male", ["He is|He's"]),
                self.create_quiz("en", "fi", "He is|He's", ["Hän on|On;male"])
            ],
            concept.quizzes("fi", "en")
        )
