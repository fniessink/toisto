"""Quiz unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.language.label import Label, Labels
from toisto.model.quiz.quiz_type import (
    ABBREVIATION,
    AFFIRMATIVE,
    ANSWER,
    ANTONYM,
    CARDINAL,
    COMPARATIVE_DEGREE,
    DECLARATIVE,
    DICTATE,
    DIMINUTIVE,
    FEMININE,
    FIRST_PERSON,
    FULL_FORM,
    IMPERATIVE,
    INFINITIVE,
    INTERPRET,
    INTERROGATIVE,
    MASCULINE,
    NEGATIVE,
    NEUTER,
    ORDER,
    ORDINAL,
    PAST_PERFECT_TENSE,
    PAST_TENSE,
    PLURAL,
    POSITIVE_DEGREE,
    PRESENT_PERFECT_TENSE,
    PRESENT_TENSE,
    READ,
    SECOND_PERSON,
    SINGULAR,
    SUPERLATIVE_DEGREE,
    THIRD_PERSON,
    VERBAL_NOUN,
    WRITE,
)
from toisto.persistence.spelling_alternatives import load_spelling_alternatives

from ....base import EN_NL, FI_EN, FI_NL, NL_FI, LabelDict, ToistoTestCase


class QuizTestCase(ToistoTestCase):
    """Base class for unit tests for the quiz class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        super().setUp()
        self.concept = self.create_concept("english", {})
        self.quiz = self.create_quiz(self.concept, Label(FI, "englanti"), [Label(NL, "Engels")])


class QuizTest(QuizTestCase):
    """Unit tests for the quiz class."""

    def setUp(self):
        """Set up fixtures."""
        super().setUp()
        self.engels = Label(NL, "Engels")
        self.een = Label(NL, "Een")
        self.huis = Label(NL, "het huis")

    def test_defaults(self):
        """Test default values of optional attributes."""
        self.assertEqual(READ, self.quiz.quiz_type)
        self.assertEqual((), self.quiz.blocked_by)
        self.assertEqual((), self.quiz.question_meanings)
        self.assertEqual((), self.quiz.answer_meanings)

    def test_repr(self):
        """Test the repr() function."""
        self.assertEqual("fi:nl:englanti:Engels:read", repr(self.quiz))

    def test_old_key(self):
        """Test the old key property."""
        self.assertEqual("english:fi:nl:englanti:read", self.quiz.old_key)

    def test_is_correct(self):
        """Test a correct guess."""
        self.assertTrue(self.quiz.is_correct(self.engels, FI_NL))

    def test_is_not_correct(self):
        """Test an incorrect guess."""
        self.assertFalse(self.quiz.is_correct(Label(NL, "engles"), FI_NL))

    def test_upper_case_answer_is_correct(self):
        """Test that an upper case answer for a lower case question is correct."""
        quiz = self.create_quiz(self.create_concept("house", {}), Label(FI, "talo"), [Label(NL, "het huis")])
        self.assertTrue(quiz.is_correct(Label(NL, "Het huis"), FI_NL))

    def test_lower_case_answer_is_correct(self):
        """Test that a lower case answer to an upper case question is correct, if source language == answer language."""
        self.assertTrue(self.quiz.is_correct(Label(NL, "engels"), FI_NL))

    def test_case_matches_for_read_and_interpret_quizzes(self):
        """Test that a lower case answer is incorrect when the answer should be upper case, and vice versa."""
        concept = self.create_concept("finnish", {})
        suomi = Label(FI, "suomi")
        suomi_finland = Label(FI, "Suomi")
        het_fins = Label(NL, "het Fins")
        for quiz_type in (READ, INTERPRET):
            quiz = self.create_quiz(concept, suomi, [het_fins], quiz_type)
            self.assertTrue(quiz.is_correct(Label(NL, "Fins"), FI_NL), quiz)
            self.assertTrue(quiz.is_correct(Label(NL, "fins"), FI_NL), quiz)

            quiz = self.create_quiz(concept, het_fins, [suomi], quiz_type)
            self.assertTrue(quiz.is_correct(suomi_finland, NL_FI))
            self.assertTrue(quiz.is_correct(suomi, NL_FI))

    def test_case_matches_for_listen_quizzes(self):
        """Test that a lower case answer is incorrect when the answer should be upper case, and vice versa."""
        concept = self.create_concept("finnish", {})
        suomi = Label(FI, "suomi")
        quiz = self.create_quiz(concept, suomi, [suomi])
        self.assertFalse(quiz.is_correct(Label(FI, "Suomi"), FI_NL))
        self.assertTrue(quiz.is_correct(suomi, FI_NL))
        self.assertTrue(quiz.is_correct(Label(FI, "suomi"), FI_NL))
        het_fins = Label(NL, "het Fins")
        quiz = self.create_quiz(concept, het_fins, [het_fins], WRITE)
        self.assertFalse(quiz.is_correct(Label(NL, "fins"), NL_FI))
        self.assertTrue(quiz.is_correct(Label(NL, "Fins"), NL_FI))

    def test_get_answer(self):
        """Test that the answer is returned."""
        self.assertEqual(self.engels, self.quiz.answer)

    def test_get_first_answer(self):
        """Test that the first answer is returned when there are multiple."""
        quiz = self.create_quiz(self.concept, Label(FI, "Yksi"), [Label(NL, "Een"), Label(NL, "Eén")])
        self.assertEqual(self.een, quiz.answer)

    def test_other_answers(self):
        """Test that the other answers can be retrieved."""
        quiz = self.create_quiz(
            self.concept,
            Label(FI, "Yksi"),
            [Label(NL, "Een"), Label(NL, "Eén", tip="tip should be ignored")],
        )
        self.assertEqual(("Eén",), quiz.other_answers(self.een).as_strings)

    def test_no_other_answers_when_quiz_type_is_listen(self):
        """Test that the other answers are not returned if the quiz type is dictate."""
        quiz = self.create_quiz(
            self.concept,
            Label(FI, "Yksi"),
            [Label(NL, "Een"), Label(NL, "Eén", tip="tip should be ignored")],
            DICTATE,
        )
        self.assertEqual((), quiz.other_answers(self.een))

    def test_no_generated_spelling_alternatives_as_other_answer(self):
        """Test that the other answers do not include generated spelling alternatives."""
        quiz = self.create_quiz(self.concept, Label(FI, "talo"), [Label(NL, "het huis")])
        self.assertEqual((), quiz.other_answers(self.huis))

    def test_tips_and_notes(self):
        """Test that the tip is added to the instruction, the notes are not, and neither are added to the question."""
        questions = [
            Label(EN, "You are", tip="singular"),
            Label(EN, "You are", tip="singular", notes=("post quiz note",)),
            Label(EN, "You are", notes=("post quiz note",)),
            Label(EN, "You are", notes=("post quiz note 1", "post quiz note 2")),
        ]
        for question in questions:
            quiz = self.create_quiz(self.concept, question, [Label(NL, "Jij bent")])
            hint = " (singular)" if question.tip == "singular" else ""
            self.assertEqual(f"Translate into Dutch{hint}", quiz.instruction)
            self.assertEqual(Label(EN, "You are"), quiz.question)

    def test_tip_is_ignored_in_answer(self):
        """Test that a tip in the answer is ignored."""
        you_are = Label(EN, "You are")
        quiz = self.create_quiz(self.concept, Label(NL, "Jij bent", tip="singular"), [you_are])
        self.assertEqual(you_are, quiz.answer)

    def test_all_notes_are_shown(self):
        """Test that all notes are shown."""
        answers = [Label(NL, "want", notes=("explain want",)), Label(NL, "omdat", notes=("explain omdat",))]
        quiz = self.create_quiz(self.concept, Label(EN, "because"), answers, WRITE)
        self.assertEqual(("explain want", "explain omdat"), quiz.notes)


class OrderQuizTest(QuizTestCase):
    """Unit tests for word order quizzes."""

    def test_order_question(self):
        """Test that the order of the words in the question is random."""
        label = Label(EN, "We eat breakfast in the kitchen.")
        quiz = self.create_quiz(self.concept, label, [label], ORDER)
        questions: set[str] = set()
        while len(questions) <= 1:  # Continue until we have two questions with different word order
            questions.add(str(quiz.question))
        for question in questions:
            # Check that the questions have the correct words
            self.assertEqual(set(str(label).split(" ")), set(question.split(" ")))

    def test_order_answer(self):
        """Test that all spelling alternatives are correct answers."""
        labels = ["We eat breakfast in the kitchen.", "In the kitchen we eat breakfast."]
        quiz = self.create_quiz(self.concept, Label(EN, labels[0]), [Label(EN, labels)], ORDER)
        for label in labels:
            self.assertTrue(quiz.is_correct(Label(EN, label), EN_NL))


class QuizInstructionTest(QuizTestCase):
    """Unit tests for quiz instructions."""

    def test_instructions(self):
        """Test the instructions."""
        expected_instructions = {
            READ: "Translate into Dutch",
            WRITE: "Translate into Finnish",
            DICTATE: "Listen and write in Finnish",
            INTERPRET: "Listen and write in Dutch",
            ANSWER: "Give the [underline]answer[/underline] in Finnish",
            ANTONYM: "Give the [underline]antonym[/underline] in Finnish",
            ORDER: "Give the [underline]right order[/underline] of the words in Finnish",
            PLURAL: "Give the [underline]plural[/underline] in Finnish",
            SINGULAR: "Give the [underline]singular[/underline] in Finnish",
            DIMINUTIVE: "Give the [underline]diminutive[/underline] in Finnish",
            MASCULINE: "Give the [underline]masculine[/underline] in Finnish",
            FEMININE: "Give the [underline]feminine[/underline] in Finnish",
            NEUTER: "Give the [underline]neuter[/underline] in Finnish",
            POSITIVE_DEGREE: "Give the [underline]positive degree[/underline] in Finnish",
            COMPARATIVE_DEGREE: "Give the [underline]comparative degree[/underline] in Finnish",
            SUPERLATIVE_DEGREE: "Give the [underline]superlative degree[/underline] in Finnish",
            FIRST_PERSON: "Give the [underline]first person[/underline] in Finnish",
            SECOND_PERSON: "Give the [underline]second person[/underline] in Finnish",
            THIRD_PERSON: "Give the [underline]third person[/underline] in Finnish",
            INFINITIVE: "Give the [underline]infinitive[/underline] in Finnish",
            VERBAL_NOUN: "Give the [underline]verbal noun[/underline] in Finnish",
            PRESENT_TENSE: "Give the [underline]present tense[/underline] in Finnish",
            PAST_TENSE: "Give the [underline]past tense[/underline] in Finnish",
            PRESENT_PERFECT_TENSE: "Give the [underline]present perfect tense[/underline] in Finnish",
            PAST_PERFECT_TENSE: "Give the [underline]past perfect tense[/underline] in Finnish",
            DECLARATIVE: "Give the [underline]declarative[/underline] in Finnish",
            INTERROGATIVE: "Give the [underline]interrogative[/underline] in Finnish",
            IMPERATIVE: "Give the [underline]imperative[/underline] in Finnish",
            AFFIRMATIVE: "Give the [underline]affirmative[/underline] in Finnish",
            NEGATIVE: "Give the [underline]negative[/underline] in Finnish",
            CARDINAL: "Give the [underline]cardinal[/underline] in Finnish",
            ORDINAL: "Give the [underline]ordinal[/underline] in Finnish",
            ABBREVIATION: "Give the [underline]abbreviation[/underline] in Finnish",
            FULL_FORM: "Give the [underline]full form[/underline] in Finnish",
        }
        for quiz_type, expected_instruction in expected_instructions.items():
            quiz = self.create_quiz(
                self.concept,
                Label(FI, "Hei"),
                [Label(NL if expected_instruction.endswith("Dutch") else FI, "Hei hei")],
                quiz_type,
            )
            self.assertEqual(expected_instruction, quiz.instruction)

    def test_instruction_complete_sentence(self):
        """Test the instruction for a complete sentence."""
        sentence = Label(EN, "Sentence.")
        quiz = self.create_quiz(self.concept, sentence, [sentence], DICTATE)
        self.assertEqual("Listen and write a complete sentence in English", quiz.instruction)

    def test_tip_is_not_shown_when_question_and_answer_language_are_the_same(self):
        """Test that a tip is not shown if the question and answer languages are the same."""
        quiz = self.create_quiz(self.concept, Label(FI, "Hän on", tip="some tip"), [Label(FI, "He ovat")], PLURAL)
        self.assertEqual("Give the [underline]plural[/underline] in Finnish", quiz.instruction)

    def test_tip_is_shown_when_question_language_equals_answer_language_and_quiz_type_is_dictate(self):
        """Test that a tip is shown if the question and answer languages are the same and the quiz type is dictate."""
        suomi = Label(FI, "Suomi", tip="country")
        quiz = self.create_quiz(self.concept, suomi, [suomi], DICTATE)
        self.assertEqual("Listen and write in Finnish (country)", quiz.instruction)

    def test_tip_is_shown_when_question_language_equals_answer_language_and_quiz_type_is_answer(self):
        """Test that a tip is shown if the question and answer languages are the same and the quiz type is answer."""
        quiz = self.create_quiz(
            self.concept,
            Label(FI, "Onko hän Bob?", tip="positive or negative"),
            [Label(FI, "On"), Label(FI, "Ei")],
            ANSWER,
        )
        self.assertEqual("Give the [underline]answer[/underline] in Finnish (positive or negative)", quiz.instruction)

    def test_colloquial_labels_get_an_automatic_tip_when_quiz_type_is_dictate(self):
        """Test that colloquial labels get an automatic tip."""
        seittemän = Label(FI, "seittemän", colloquial=True)
        seitsemän = Label(FI, "seitsemän")
        quiz = self.create_quiz(self.concept, seittemän, [seitsemän], DICTATE)
        self.assertEqual("Listen to the colloquial Finnish and write in standard Finnish", quiz.instruction)

    def test_colloquial_labels_get_an_automatic_tip_when_quiz_type_is_interpret(self):
        """Test that colloquial labels get an automatic tip."""
        quiz = self.create_quiz(self.concept, Label(FI, "seittemän", colloquial=True), [Label(NL, "zeven")], INTERPRET)
        self.assertEqual("Listen to the colloquial Finnish and write in Dutch", quiz.instruction)

    def test_sentences_get_an_automatic_tip_when_quiz_type_is_listen(self):
        """Test that sentences get an automatic tip when the quiz type is a listen quiz."""
        quiz = self.create_quiz(self.concept, Label(FI, "Terve!"), [Label(NL, "Hallo!")], INTERPRET)
        self.assertEqual("Listen and write a complete sentence in Dutch", quiz.instruction)

    def test_homographs_get_an_automatic_tip_based_on_the_hypernym(self):
        """Test that homographs get an automatic tip based on the hypernym."""
        bank_nl: LabelDict = {"label": "de bank", "language": NL}
        # Create the homograph of sofa:
        self.create_concept("bank (finance)", labels=[{"label": "pankki", "language": FI}, bank_nl])
        # Create the hypernym of sofa:
        self.create_concept(
            "furniture",
            labels=[{"label": "het meubilair", "language": NL, "note": "this should not be shown as part of the note"}],
        )
        sofa = self.create_concept(
            "bank",
            {"hypernym": "furniture"},
            labels=[{"label": "sofa", "language": FI}, bank_nl],
        )
        bank_label = Label(NL, "de bank")
        quiz = self.create_quiz(sofa, bank_label, [bank_label], DICTATE)
        self.assertEqual("Listen and write in Dutch (het meubilair)", quiz.instruction)

    def test_non_homographs_do_not_get_an_automatic_tip_based_on_the_hypernym(self):
        """Test that concepts that are not homograph do not get an automatic tip based on the hypernym."""
        fly_en: LabelDict = {"label": "fly", "language": EN}
        # Create the homograph of fly:
        self.create_concept("to fly", labels=[fly_en, {"label": "vliegen", "language": NL}])
        self.create_concept("insect", {})  # Create the hypernym of fly
        fly = self.create_concept("fly", {"hypernym": "insect"}, labels=[fly_en, {"label": "de vlieg", "language": NL}])
        vlieg = Label(NL, "de vlieg")
        quiz = self.create_quiz(fly, vlieg, [vlieg], DICTATE)
        self.assertEqual("Listen and write in Dutch", quiz.instruction)

    def test_homographs_get_an_automatic_tip_based_on_only_the_first_hypernym(self):
        """Test that homographs get an automatic tip based on the first hypernym if there are multiple."""
        bank_nl: LabelDict = {"label": "de bank", "language": NL}
        # Create the homograph of sofa:
        self.create_concept("bank (finance)", labels=[{"label": "pankki", "language": FI}, bank_nl])
        # Create the hypernym of seating:
        self.create_concept("furniture", {})
        # Create the hypernym of sofa:
        self.create_concept("seating", {"hypernym": "furniture"}, labels=[{"label": "het zitmeubel", "language": NL}])
        sofa = self.create_concept(
            "sofa", {"hypernym": "seating"}, labels=[{"label": "sohva", "language": FI}, bank_nl]
        )
        bank_label = Label(NL, "de bank")
        quiz = self.create_quiz(sofa, bank_label, [bank_label], DICTATE)
        self.assertEqual("Listen and write in Dutch (het zitmeubel)", quiz.instruction)

    def test_homographs_get_an_automatic_tip_based_on_the_common_base_concept(self):
        """Test that homographs get an automatic tip based on the common base concept."""
        concept = self.create_verb_with_grammatical_number_and_person()
        second_person_singular = next(
            leaf_concept
            for leaf_concept in concept.leaf_concepts(EN)
            if leaf_concept.concept_id == "to have/singular/second person"
        )
        quiz = self.create_quiz(second_person_singular, Label(EN, "you have"), [Label(NL, "jij hebt")], INTERPRET)
        self.assertEqual("Listen and write in Dutch (singular)", quiz.instruction)

    def test_homographs_get_an_automatic_tip_based_on_the_common_base_concept_when_more_than_two_homographs(self):
        """Test that homographs get an automatic tip based on the common base concept."""
        concept = self.create_concept(
            "to read",
            labels=[
                {
                    "label": {
                        "present tense": {
                            "singular": {"second person": "you read"},
                            "plural": {"second person": "you read"},
                        },
                        "past tense": {
                            "singular": {"second person": "you read"},
                            "plural": {"second person": "you read"},
                        },
                    },
                    "language": EN,
                },
                {
                    "label": {
                        "present tense": {
                            "singular": {"second person": "jij leest"},
                            "plural": {"second person": "jullie lezen"},
                        },
                        "past tense": {
                            "singular": {"second person": "jij las"},
                            "plural": {"second person": "jullie lazen"},
                        },
                    },
                    "language": NL,
                },
            ],
        )
        second_person_singular = next(
            leaf_concept
            for leaf_concept in concept.leaf_concepts(EN)
            if leaf_concept.concept_id == "to read/present tense/singular/second person"
        )
        quiz = self.create_quiz(second_person_singular, Label(EN, "you read"), [Label(NL, "jij leest")], INTERPRET)
        self.assertEqual("Listen and write in Dutch (present tense; singular)", quiz.instruction)

    def test_homographs_get_an_automatic_tip_based_on_the_holonym(self):
        """Test that homographs get an automatic tip based on the holonym."""
        self.create_concept(
            "tree",
            labels=[
                {"label": "puu", "language": FI, "note": "this should not be shown as part of the note"},
                {"label": "de boom", "language": NL},
            ],
        )
        wood = self.create_concept(
            "wood",
            {"holonym": "tree"},
            labels=[{"label": "puu", "language": FI}, {"label": "het hout", "language": NL}],
        )
        hout = Label(NL, "het hout")
        puu = Label(FI, "puu")
        write_quiz = self.create_quiz(wood, puu, [hout], WRITE)
        self.assertEqual("Translate into Dutch (part of 'puu')", write_quiz.instruction)
        dictate_quiz = self.create_quiz(wood, puu, [hout], INTERPRET)
        self.assertEqual("Listen and write in Dutch (part of 'puu')", dictate_quiz.instruction)
        read_quiz = self.create_quiz(wood, puu, [hout], READ)
        self.assertEqual("Translate into Dutch (part of 'puu')", read_quiz.instruction)

    def test_homographs_get_an_automatic_tip_based_on_the_involved_concept(self):
        """Test that homographs get an automatic tip based on the involved concept."""
        play_en: LabelDict = {"label": "to play", "language": EN}
        self.create_concept(
            "sport", labels=[{"label": "sport", "language": EN, "note": "this should not be shown as part of the note"}]
        )
        play_instrument = self.create_concept("to play a musical instrument", labels=[play_en])
        play_sport = self.create_concept(
            "to play a sport",
            {"involves": "sport"},
            labels=[play_en, {"label": "pelata", "language": FI}],
        )
        write_quiz = self.create_quiz(play_sport, Label(EN, "to play"), [Label(FI, "pelata")], WRITE)
        self.assertEqual("Translate into Finnish (involves 'sport')", write_quiz.instruction)
        write_quiz = self.create_quiz(play_instrument, Label(EN, "to play"), [Label(FI, "soittaa")], WRITE)
        self.assertEqual("Translate into Finnish", write_quiz.instruction)

    def test_capitonyms_get_an_automatic_tip_based_on_the_hypernym(self):
        """Test that capitonyms get an automatic tip based on the hypernym, for listening quizzes."""
        self.create_concept(
            "greece", labels=[{"label": "Kreikka", "language": FI}, {"label": "Griekenland", "language": NL}]
        )
        self.create_concept("language", labels=[{"label": "kieli", "language": FI}])
        greek = self.create_concept(
            "greek",
            {"hypernym": "language"},
            labels=[{"label": "kreikka", "language": FI}, {"label": "Grieks", "language": NL}],
        )
        kreikka = Label(FI, "kreikka")
        quiz = self.create_quiz(greek, kreikka, [kreikka], DICTATE)
        self.assertEqual("Listen and write in Finnish (kieli)", quiz.instruction)
        quiz = self.create_quiz(greek, kreikka, [Label(NL, "Grieks")], READ)
        self.assertEqual("Translate into Dutch", quiz.instruction)

    def test_capitonyms_get_an_automatic_tip_based_on_only_the_first_hypernym(self):
        """Test that capitonyms get an automatic tip based on the first hypernym if there are multiple."""
        # Create the capitonym of greek:
        self.create_concept(
            "greece", labels=[{"label": "Kreikka", "language": FI}, {"label": "Griekenland", "language": NL}]
        )
        self.create_concept("language", {})  # Create the hypernym of Indo-European language
        # Create the hypernym of greek:
        self.create_concept(
            "Indo-European language",
            {"hypernym": "language"},
            labels=[{"label": "indoeurooppalainen kieli", "language": FI}],
        )
        greek = self.create_concept(
            "greek",
            {"hypernym": "Indo-European language"},
            labels=[{"label": "kreikka", "language": FI}, {"label": "Grieks", "language": NL}],
        )
        kreikka = Label(FI, "kreikka")
        quiz = self.create_quiz(greek, kreikka, [kreikka], DICTATE)
        self.assertEqual("Listen and write in Finnish (indoeurooppalainen kieli)", quiz.instruction)

    def test_capitonyms_get_an_automatic_tip_based_on_the_common_base_concept(self):
        """Test that capitonyms get an automatic tip based on the common base concept."""
        concept = self.create_concept(
            "to be",
            labels=[
                {
                    "label": {"singular": {"second person": "Te olette"}, "plural": {"second person": "te olette"}},
                    "language": FI,
                },
                {
                    "label": {"singular": {"second person": "u bent"}, "plural": {"second person": "jullie zijn"}},
                    "language": NL,
                },
            ],
        )
        second_person_singular = next(
            leaf_concept
            for leaf_concept in concept.leaf_concepts(FI)
            if leaf_concept.concept_id == "to be/singular/second person"
        )
        quiz = self.create_quiz(second_person_singular, Label(FI, "Te olette"), [Label(NL, "u bent")], INTERPRET)
        self.assertEqual("Listen and write in Dutch (singular)", quiz.instruction)


class QuizSpellingAlternativesTests(QuizTestCase):
    """Unit tests for checking spelling alternatives."""

    def test_spelling_alternative_of_answer(self):
        """Test that a quiz can deal with alternative spellings of answers."""
        quiz = self.create_quiz(self.concept, Label(FI, "yksi"), [Label(NL, ["een", "één"])])
        self.assertEqual(Label(NL, "een"), quiz.answer)

    def test_spelling_alternative_of_question(self):
        """Test that a quiz can deal with alternative spellings of the question."""
        quiz = self.create_quiz(self.concept, Label(NL, ["een", "één"]), [Label(FI, "yksi")])
        self.assertEqual(Label(NL, "een"), quiz.question)

    def test_spelling_alternative_is_correct(self):
        """Test that an answer that matches a spelling alternative is correct."""
        quiz = self.create_quiz(self.concept, Label(FI, "Yksi."), [Label(NL, ["Een", "Eén"]), Label(NL, "één")])
        for alternative in ("Een", "Eén", "één"):
            self.assertTrue(quiz.is_correct(Label(NL, alternative), FI_NL))

    def test_other_answers_with_spelling_alternatives(self):
        """Test the spelling alternatives are returned as other answers."""
        quiz = self.create_quiz(self.concept, Label(FI, "Yksi."), [Label(NL, ["Een", "Eén"]), Label(NL, "één")])
        alternatives = ("Een", "Eén", "één")
        for alternative in alternatives:
            other_answers = list(alternatives)
            other_answers.remove(alternative)
            answer = Label(NL, alternative)
            self.assertEqual(Labels(Label(NL, answer) for answer in other_answers), quiz.other_answers(answer))

    def test_generated_spelling_alternative_is_correct(self):
        """Test that a generated spelling alternative is accepted as answer."""
        load_spelling_alternatives(EN_NL)
        quiz = self.create_quiz(self.concept, Label(NL, "Het is waar."), [Label(EN, "It is true.")])
        self.assertTrue(quiz.is_correct(Label(EN, "It's true"), EN_NL))
        quiz = self.create_quiz(self.concept, Label(NL, "Het is."), [Label(EN, "It is.")])
        self.assertTrue(quiz.is_correct(Label(EN, "It's."), EN_NL))
        quiz = self.create_quiz(self.concept, Label(NL, "Ik ben Alice."), [Label(EN, "I am Alice.")])
        self.assertTrue(quiz.is_correct(Label(EN, "I'm Alice."), EN_NL))
        quiz = self.create_quiz(self.concept, Label(NL, "Ik overval."), [Label(EN, "I ambush.")])
        self.assertFalse(quiz.is_correct(Label(EN, "I'mbush."), EN_NL))
        quiz = self.create_quiz(self.concept, Label(EN, "house"), [Label(NL, "het huis")])
        self.assertTrue(quiz.is_correct(Label(NL, "huis"), EN_NL))
        quiz = self.create_quiz(self.concept, Label(EN, "I am"), [Label(FI, "minä olen")])
        self.assertTrue(quiz.is_correct(Label(FI, "olen"), FI_EN))
        quiz = self.create_quiz(self.concept, Label(EN, "I am Alice."), [Label(FI, "Minä olen Alice.")])
        self.assertTrue(quiz.is_correct(Label(FI, "Olen Alice."), FI_EN))

    def test_generated_spelling_alternative_is_no_other_answer(self):
        """Test that a generated spelling alternative is not an other answer."""
        load_spelling_alternatives(EN_NL)
        quiz = self.create_quiz(self.concept, Label(EN, "pain"), [Label(NL, "de pijn")])
        answer = Label(NL, "pijn")
        self.assertTrue(quiz.is_correct(answer, EN_NL))
        self.assertEqual((), quiz.other_answers(answer))

    def test_capitalized_answer_without_article(self):
        """Test that the article can be left out, even though the noun starts with a capital."""
        load_spelling_alternatives(FI_NL)
        quiz = self.create_quiz(self.concept, Label(FI, "englanti"), [Label(NL, "het Engels")])
        answer = Label(NL, "Engels")
        self.assertTrue(quiz.is_correct(answer, FI_NL))


class QuizEqualityTests(QuizTestCase):
    """Unit tests for the equality of quiz instances."""

    def test_equal(self):
        """Test that a quiz is equal to itself and to quizzes with the same parameters."""
        self.assertEqual(self.quiz, self.quiz)
        self.assertEqual(self.copy_quiz(self.quiz), self.quiz)

    def test_equal_with_different_notes(self):
        """Test that quizzes are equal if only their notes differ."""
        self.assertEqual(self.copy_quiz(self.quiz, question=Label(FI, "englanti", notes=("note",))), self.quiz)
        self.assertEqual(self.copy_quiz(self.quiz, answers=[Label(NL, "Engels", notes=("note",))]), self.quiz)

    def test_not_equal_with_different_questions(self):
        """Test that quizzes are not equal if only their questions differ."""
        self.assertNotEqual(self.copy_quiz(self.quiz, question=Label(FI, "Saksa")), self.quiz)

    def test_not_equal_with_different_answers(self):
        """Test that quizzes are not equal if only their answers differ."""
        self.assertNotEqual(self.copy_quiz(self.quiz, answers=[Label(NL, "Duits")]), self.quiz)

    def test_not_equal_with_different_quiz_types(self):
        """Test that quizzes are not equal if only their quiz types differ."""
        self.assertNotEqual(self.copy_quiz(self.quiz, quiz_type=DICTATE), self.quiz)

    def test_not_equal_when_questions_have_different_case(self):
        """Test that quizzes are different if only the case of the question differs."""
        self.assertNotEqual(
            self.copy_quiz(self.quiz, question=Label(self.quiz.question.language, str(self.quiz.question).upper())),
            self.quiz,
        )

    def test_not_equal_when_answers_have_different_case(self):
        """Test that quizzes are not equal if only the case of the answers differs."""
        answers = [answer.lower_case for answer in self.quiz.answers]
        self.assertNotEqual(self.copy_quiz(self.quiz, answers=answers), self.quiz)
