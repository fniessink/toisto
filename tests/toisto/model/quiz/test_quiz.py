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
    FEMALE,
    FIRST_PERSON,
    FULL_FORM,
    IMPERATIVE,
    INFINITIVE,
    INTERPRET,
    INTERROGATIVE,
    MALE,
    NEGATIVE,
    NEUTER,
    ORDER,
    ORDINAL,
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
    WRITE,
)
from toisto.persistence.spelling_alternatives import load_spelling_alternatives

from ....base import EN_FI, EN_NL, FI_EN, FI_NL, NL_EN, NL_FI, ToistoTestCase


class QuizTestCase(ToistoTestCase):
    """Base class for unit tests for the quiz class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        super().setUp()
        self.concept = self.create_concept("english", {})
        self.language_pair = FI_NL
        self.quiz = self.create_quiz(self.concept, "Englanti", ["Engels"])


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
        self.assertEqual("english:fi:nl:Englanti:read", repr(self.quiz))

    def test_is_correct(self):
        """Test a correct guess."""
        self.assertTrue(self.quiz.is_correct(self.engels, self.language_pair))

    def test_is_not_correct(self):
        """Test an incorrect guess."""
        self.assertFalse(self.quiz.is_correct(Label(NL, "engles"), self.language_pair))

    def test_upper_case_answer_is_correct(self):
        """Test that an upper case answer for a lower case question is correct."""
        quiz = self.create_quiz(self.create_concept("house", {}), "talo", ["het huis"])
        self.assertTrue(quiz.is_correct(Label(NL, "Het huis"), self.language_pair))

    def test_lower_case_answer_is_correct(self):
        """Test that a lower case answer to an upper case question is correct, if source language == answer language."""
        self.assertTrue(self.quiz.is_correct(Label(NL, "engels"), self.language_pair))

    def test_case_matches_for_read_and_interpret_quizzes(self):
        """Test that a lower case answer is incorrect when the answer should be upper case, and vice versa."""
        concept = self.create_concept("finnish", {})

        for quiz_type in (READ, INTERPRET):
            quiz = self.create_quiz(concept, "suomi", ["het Fins"], quiz_type, language_pair=FI_NL)
            self.assertTrue(quiz.is_correct(Label(NL, "Fins"), FI_NL), quiz)
            self.assertTrue(quiz.is_correct(Label(NL, "fins"), FI_NL), quiz)

            quiz = self.create_quiz(concept, "het Fins", ["suomi"], quiz_type, language_pair=NL_FI)
            self.assertTrue(quiz.is_correct(Label(FI, "Suomi"), NL_FI))
            self.assertTrue(quiz.is_correct(Label(FI, "suomi"), NL_FI))

    def test_case_matches_for_listen_quizzes(self):
        """Test that a lower case answer is incorrect when the answer should be upper case, and vice versa."""
        concept = self.create_concept("finnish", {})

        quiz = self.create_quiz(concept, "suomi", ["suomi"], language_pair=FI_NL)
        self.assertFalse(quiz.is_correct(Label(FI, "Suomi"), FI_NL))
        self.assertTrue(quiz.is_correct(Label(FI, "suomi"), FI_NL))

        quiz = self.create_quiz(concept, "het Fins", ["het Fins"], WRITE, language_pair=NL_FI)
        self.assertFalse(quiz.is_correct(Label(NL, "fins"), NL_FI))
        self.assertTrue(quiz.is_correct(Label(NL, "Fins"), NL_FI))

    def test_get_answer(self):
        """Test that the answer is returned."""
        self.assertEqual(self.engels, self.quiz.answer)

    def test_get_first_answer(self):
        """Test that the first answer is returned when there are multiple."""
        quiz = self.create_quiz(self.concept, "Yksi", ["Een", "Eén"])
        self.assertEqual(self.een, quiz.answer)

    def test_other_answers(self):
        """Test that the other answers can be retrieved."""
        quiz = self.create_quiz(self.concept, "Yksi", ["Een", "Eén;note should be ignored"])
        self.assertEqual(("Eén",), quiz.other_answers(self.een).as_strings)

    def test_no_other_answers_when_quiz_type_is_listen(self):
        """Test that the other answers are not returned if the quiz type is dictate."""
        quiz = self.create_quiz(self.concept, "Yksi", ["Een", "Eén;note should be ignored"], DICTATE)
        self.assertEqual((), quiz.other_answers(self.een))

    def test_no_generated_spelling_alternatives_as_other_answer(self):
        """Test that the other answers do not include generated spelling alternatives."""
        quiz = self.create_quiz(self.concept, "talo", ["het huis"])
        self.assertEqual((), quiz.other_answers(self.huis))

    def test_note(self):
        """Test that the first note is added to the instruction, the second is not, and neither to the question."""
        self.language_pair = EN_NL
        for question in (
            "You are;singular",
            "You are;singular;post quiz note",
            "You are;;post quiz note",
            "You are;;post quiz note 1;post quiz note 2",
        ):
            quiz = self.create_quiz(self.concept, question, ["Jij bent|Je bent"])
            hint = " (singular)" if "singular" in question else ""
            self.assertEqual(f"Translate into Dutch{hint}", quiz.instruction)
            self.assertEqual(Label(EN, "You are"), quiz.question)

    def test_question_note_is_ignored_in_answer(self):
        """Test that a note in the answer is ignored."""
        self.language_pair = NL_EN
        quiz = self.create_quiz(self.concept, "Jij bent", ["You are;singular"])
        self.assertEqual(Label(EN, "You are"), quiz.answer)

    def test_all_answer_notes_are_shown(self):
        """Test that all answer notes are shown."""
        self.language_pair = EN_NL
        answers = ["want;;explain want", "omdat;;explain omdat"]
        quiz = self.create_quiz(self.concept, "because", answers, WRITE)
        self.assertEqual(("explain want", "explain omdat"), quiz.answer_notes)


class OrderQuizTest(QuizTestCase):
    """Unit tests for word order quizzes."""

    def test_order_question(self):
        """Test that the order of the words in the question is random."""
        self.language_pair = EN_NL
        label = "We eat breakfast in the kitchen."
        quiz = self.create_quiz(self.concept, label, [label], ORDER)
        questions: set[str] = set()
        while len(questions) <= 1:  # Continue until we have two questions with different word order
            questions.add(str(quiz.question))
        for question in questions:
            # Check that the questions have the correct words
            self.assertEqual(set(label.split(" ")), set(question.split(" ")))

    def test_order_answer(self):
        """Test that all spelling alternatives are correct answers."""
        self.language_pair = EN_NL
        labels = ["We eat breakfast in the kitchen.", "In the kitchen we eat breakfast."]
        quiz = self.create_quiz(self.concept, labels[0], ["|".join(labels)], ORDER)
        for label in labels:
            self.assertTrue(quiz.is_correct(Label(EN, label), self.language_pair))


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
            MALE: "Give the [underline]male[/underline] in Finnish",
            FEMALE: "Give the [underline]female[/underline] in Finnish",
            NEUTER: "Give the [underline]neuter[/underline] in Finnish",
            POSITIVE_DEGREE: "Give the [underline]positive degree[/underline] in Finnish",
            COMPARATIVE_DEGREE: "Give the [underline]comparative degree[/underline] in Finnish",
            SUPERLATIVE_DEGREE: "Give the [underline]superlative degree[/underline] in Finnish",
            FIRST_PERSON: "Give the [underline]first person[/underline] in Finnish",
            SECOND_PERSON: "Give the [underline]second person[/underline] in Finnish",
            THIRD_PERSON: "Give the [underline]third person[/underline] in Finnish",
            INFINITIVE: "Give the [underline]infinitive[/underline] in Finnish",
            PRESENT_TENSE: "Give the [underline]present tense[/underline] in Finnish",
            PAST_TENSE: "Give the [underline]past tense[/underline] in Finnish",
            PRESENT_PERFECT_TENSE: "Give the [underline]present perfect tense[/underline] in Finnish",
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
            quiz = self.create_quiz(self.concept, "Hei", ["Hei hei"], quiz_type)
            self.assertEqual(expected_instruction, quiz.instruction)

    def test_instruction_complete_sentence(self):
        """Test the instruction for a complete sentence."""
        self.language_pair = EN_NL
        quiz = self.create_quiz(self.concept, "Sentence.", ["Sentence."], DICTATE)
        self.assertEqual("Listen and write a complete sentence in English", quiz.instruction)

    def test_question_note_is_not_shown_when_question_and_answer_language_are_the_same(self):
        """Test that a note is not shown if the question and answer languages are the same."""
        self.language_pair = FI_NL
        quiz = self.create_quiz(self.concept, "Hän on;female", ["He ovat"], PLURAL)
        self.assertEqual("Give the [underline]plural[/underline] in Finnish", quiz.instruction)

    def test_question_note_is_shown_when_question_language_equals_answer_language_and_quiz_type_is_dictate(self):
        """Test that a note is shown if the question and answer languages are the same and the quiz type is dictate."""
        self.language_pair = FI_NL
        quiz = self.create_quiz(self.concept, "Suomi;country", ["Finland"], DICTATE)
        self.assertEqual("Listen and write in Finnish (country)", quiz.instruction)

    def test_question_note_is_shown_when_question_language_equals_answer_language_and_quiz_type_is_answer(self):
        """Test that a note is shown if the question and answer languages are the same and the quiz type is answer."""
        self.language_pair = FI_NL
        quiz = self.create_quiz(self.concept, "Onko hän Bob?;positive or negative", ["On", "Ei"], ANSWER)
        self.assertEqual("Give the [underline]answer[/underline] in Finnish (positive or negative)", quiz.instruction)

    def test_colloquial_labels_get_an_automatic_note_when_quiz_type_is_dictate(self):
        """Test that colloquial labels get an automatic note."""
        self.language_pair = FI_NL
        quiz = self.create_quiz(self.concept, "seittemän*", ["seitsemän"], DICTATE)
        self.assertEqual("Listen to the colloquial Finnish and write in standard Finnish", quiz.instruction)

    def test_colloquial_labels_get_an_automatic_note_when_quiz_type_is_interpret(self):
        """Test that colloquial labels get an automatic note."""
        self.language_pair = FI_NL
        quiz = self.create_quiz(self.concept, "seittemän*", ["zeven"], INTERPRET)
        self.assertEqual("Listen to the colloquial Finnish and write in Dutch", quiz.instruction)

    def test_sentences_get_an_automatic_note_when_quiz_type_is_listen(self):
        """Test that sentences get an automatic note when the quiz type is a listen quiz."""
        self.language_pair = FI_NL
        quiz = self.create_quiz(self.concept, "Terve!", ["Hallo!"], INTERPRET)
        self.assertEqual("Listen and write a complete sentence in Dutch", quiz.instruction)

    def test_homographs_get_an_automatic_note_based_on_the_hypernym(self):
        """Test that homographs get an automatic note based on the hypernym."""
        self.language_pair = NL_FI
        self.create_concept("bank (finance)", {"fi": "pankki", "nl": "de bank"})  # Create the homograph of sofa
        self.create_concept("furniture", {})  # Create the hypernym of sofa
        sofa = self.create_concept("bank", {"hypernym": "furniture", "fi": "sohva", "nl": "de bank"})
        quiz = self.create_quiz(sofa, "de bank", ["sohva"], DICTATE)
        self.assertEqual("Listen and write in Dutch (furniture)", quiz.instruction)

    def test_non_homographs_do_not_get_an_automatic_note_based_on_the_hypernym(self):
        """Test that concepts that are not homograph do not get an automatic note based on the hypernym."""
        self.language_pair = NL_EN
        self.create_concept("to fly", {"en": "fly", "nl": "vliegen"})  # Create the homograph of fly
        self.create_concept("insect", {})  # Create the hypernym of fly
        fly = self.create_concept("fly", {"hypernym": "insect", "en": "fly", "nl": "de vlieg"})
        quiz = self.create_quiz(fly, "de vlieg", ["de vlieg"], DICTATE)
        self.assertEqual("Listen and write in Dutch", quiz.instruction)

    def test_homographs_get_an_automatic_note_based_on_only_the_first_hypernym(self):
        """Test that homographs get an automatic note based on the first hypernym if there are multiple."""
        self.language_pair = NL_FI
        self.create_concept("bank (finance)", {"fi": "pankki", "nl": "de bank"})  # Create the homograph of sofa
        self.create_concept("furniture", {})  # Create the hypernym of seating
        self.create_concept("seating", {"hypernym": "furniture"})  # Create the hypernym of sofa
        sofa = self.create_concept("sofa", {"hypernym": "seating", "fi": "sohva", "nl": "de bank"})
        quiz = self.create_quiz(sofa, "de bank", ["sohva"], DICTATE)
        self.assertEqual("Listen and write in Dutch (seating)", quiz.instruction)

    def test_homographs_get_an_automatic_note_based_on_the_common_base_concept(self):
        """Test that homographs get an automatic note based on the common base concept."""
        self.language_pair = EN_NL
        concept = self.create_verb_with_grammatical_number_and_person()
        second_person_singular = next(
            leaf_concept
            for leaf_concept in concept.leaf_concepts(EN)
            if leaf_concept.concept_id == "to have/singular/second person"
        )
        quiz = self.create_quiz(second_person_singular, "you have", ["jij hebt"], INTERPRET)
        self.assertEqual("Listen and write in Dutch (singular)", quiz.instruction)

    def test_homographs_get_an_automatic_note_based_on_the_common_base_concept_when_more_than_two_homographs(self):
        """Test that homographs get an automatic note based on the common base concept."""
        self.language_pair = EN_NL
        concept = self.create_concept(
            "to read",
            {
                "present tense": dict(
                    singular={"second person": dict(en="you read", nl="jij leest")},
                    plural={"second person": dict(en="you read", nl="jullie lezen")},
                ),
                "past tense": dict(
                    singular={"second person": dict(en="you read", nl="jij las")},
                    plural={"second person": dict(en="you read", nl="jullie lazen")},
                ),
            },
        )
        second_person_singular = next(
            leaf_concept
            for leaf_concept in concept.leaf_concepts(EN)
            if leaf_concept.concept_id == "to read/present tense/singular/second person"
        )
        quiz = self.create_quiz(second_person_singular, "you read", ["jij leest"], INTERPRET)
        self.assertEqual("Listen and write in Dutch (present tense; singular)", quiz.instruction)

    def test_capitonyms_get_an_automatic_note_based_on_the_hypernym(self):
        """Test that capitonyms get an automatic note based on the hypernym, for listening quizzes."""
        self.language_pair = FI_NL
        self.create_concept("greece", {"fi": "Kreikka", "nl": "Griekenland"})  # Create the capitonym of greek
        self.create_concept("language", {})  # Create the hypernym of Indo-Wuropean language
        greek = self.create_concept("greek", {"hypernym": "language", "fi": "kreikka", "nl": "Grieks"})
        quiz = self.create_quiz(greek, "kreikka", ["Grieks"], DICTATE)
        self.assertEqual("Listen and write in Finnish (language)", quiz.instruction)
        quiz = self.create_quiz(greek, "kreikka", ["Grieks"])
        self.assertEqual("Translate into Dutch", quiz.instruction)

    def test_capitonyms_get_an_automatic_note_based_on_only_the_first_hypernym(self):
        """Test that capitonyms get an automatic note based on the first hypernym if there are multiple."""
        self.language_pair = FI_NL
        self.create_concept("greece", {"fi": "Kreikka", "nl": "Griekenland"})  # Create the capitonym of greek
        self.create_concept("language", {})  # Create the hypernym of Indo-European language
        self.create_concept("Indo-European language", {"hypernym": "language"})  # Create the hypernym of greek
        greek = self.create_concept("greek", {"hypernym": "Indo-European language", "fi": "kreikka", "nl": "Grieks"})
        quiz = self.create_quiz(greek, "kreikka", ["Grieks"], DICTATE)
        self.assertEqual("Listen and write in Finnish (Indo-European language)", quiz.instruction)

    def test_capitonyms_get_an_automatic_note_based_on_the_common_base_concept(self):
        """Test that capitonyms get an automatic note based on the common base concept."""
        self.language_pair = FI_NL
        concept = self.create_concept(
            "to be",
            dict(
                singular={
                    "second person": dict(fi="Te olette", nl="u bent"),
                },
                plural={
                    "second person": dict(fi="te olette", nl="jullie zijn"),
                },
            ),
        )
        second_person_singular = next(
            leaf_concept
            for leaf_concept in concept.leaf_concepts(FI)
            if leaf_concept.concept_id == "to be/singular/second person"
        )
        quiz = self.create_quiz(second_person_singular, "Te olette", ["u bent"], INTERPRET)
        self.assertEqual("Listen and write in Dutch (singular)", quiz.instruction)


class QuizSpellingAlternativesTests(QuizTestCase):
    """Unit tests for checking spelling alternatives."""

    def test_spelling_alternative_of_answer(self):
        """Test that a quiz can deal with alternative spellings of answers."""
        quiz = self.create_quiz(self.concept, "yksi", ["een|één"])
        self.assertEqual(Label(NL, "een"), quiz.answer)

    def test_spelling_alternative_of_question(self):
        """Test that a quiz can deal with alternative spellings of the question."""
        self.language_pair = NL_FI
        quiz = self.create_quiz(self.concept, "een|één", ["yksi"])
        self.assertEqual(Label(NL, "een"), quiz.question)

    def test_spelling_alternative_is_correct(self):
        """Test that an answer that matches a spelling alternative is correct."""
        quiz = self.create_quiz(self.concept, "Yksi.", ["Een|Eén", "één"])
        for alternative in ("Een", "Eén", "één"):
            self.assertTrue(quiz.is_correct(Label(NL, alternative), FI_NL))

    def test_other_answers_with_spelling_alternatives(self):
        """Test the spelling alternatives are returned as other answers."""
        quiz = self.create_quiz(self.concept, "Yksi.", ["Een|Eén", "één"])
        alternatives = ("Een", "Eén", "één")
        for alternative in alternatives:
            other_answers = list(alternatives)
            other_answers.remove(alternative)
            answer = Label(NL, alternative)
            self.assertEqual(Labels(Label(NL, answer) for answer in other_answers), quiz.other_answers(answer))

    def test_generated_spelling_alternative_is_correct(self):
        """Test that a generated spelling alternative is accepted as answer."""
        load_spelling_alternatives(EN_NL)
        self.language_pair = NL_EN
        quiz = self.create_quiz(self.concept, "Het is waar.", ["It is true."])
        self.assertTrue(quiz.is_correct(Label(EN, "It's true"), self.language_pair))
        quiz = self.create_quiz(self.concept, "Het is.", ["It is."])
        self.assertTrue(quiz.is_correct(Label(EN, "It's."), self.language_pair))
        quiz = self.create_quiz(self.concept, "Ik ben Alice.", ["I am Alice."])
        self.assertTrue(quiz.is_correct(Label(EN, "I'm Alice."), self.language_pair))
        quiz = self.create_quiz(self.concept, "Ik overval.", ["I ambush."])
        self.assertFalse(quiz.is_correct(Label(EN, "I'mbush."), self.language_pair))
        self.language_pair = EN_NL
        quiz = self.create_quiz(self.concept, "house", ["het huis"])
        self.assertTrue(quiz.is_correct(Label(NL, "huis"), self.language_pair))
        load_spelling_alternatives(FI_EN)
        self.language_pair = EN_FI
        quiz = self.create_quiz(self.concept, "I am", ["minä olen"])
        self.assertTrue(quiz.is_correct(Label(FI, "olen"), self.language_pair))
        quiz = self.create_quiz(self.concept, "I am Alice.", ["Minä olen Alice."])
        self.assertTrue(quiz.is_correct(Label(FI, "Olen Alice."), self.language_pair))

    def test_generated_spelling_alternative_is_no_other_answer(self):
        """Test that a generated spelling alternative is not an other answer."""
        self.language_pair = EN_NL
        load_spelling_alternatives(EN_NL)
        quiz = self.create_quiz(self.concept, "pain", ["de pijn"])
        answer = Label(NL, "pijn")
        self.assertTrue(quiz.is_correct(answer, self.language_pair))
        self.assertEqual((), quiz.other_answers(answer))

    def test_capitalized_answer_without_article(self):
        """Test that the article can be left out, even though the noun starts with a capital."""
        load_spelling_alternatives(FI_NL)
        quiz = self.create_quiz(self.concept, "englanti", ["het Engels"])
        answer = Label(NL, "Engels")
        self.assertTrue(quiz.is_correct(answer, self.language_pair))


class QuizEqualityTests(QuizTestCase):
    """Unit tests for the equality of quiz instances."""

    def test_equal(self):
        """Test that a quiz is equal to itself and to quizzes with the same parameters."""
        self.assertEqual(self.quiz, self.quiz)
        self.assertEqual(self.copy_quiz(self.quiz), self.quiz)

    def test_equal_with_different_notes(self):
        """Test that quizzes are equal if only their notes differ."""
        self.assertEqual(self.copy_quiz(self.quiz, question="Englanti;note"), self.quiz)
        self.assertEqual(self.copy_quiz(self.quiz, answers=["Engels;note"]), self.quiz)

    def test_not_equal_with_different_questions(self):
        """Test that quizzes are not equal if only their questions differ."""
        self.assertNotEqual(self.copy_quiz(self.quiz, question="Saksa"), self.quiz)

    def test_equal_with_different_answers(self):
        """Test that quizzes are equal if only their answers differ."""
        self.assertEqual(self.copy_quiz(self.quiz, answers=["Duits"]), self.quiz)

    def test_not_equal_with_different_quiz_types(self):
        """Test that quizzes are not equal if only their quiz types differ."""
        self.assertNotEqual(self.copy_quiz(self.quiz, quiz_type=DICTATE), self.quiz)

    def test_not_equal_when_questions_have_different_case(self):
        """Test that quizzes are different if only the case of the question differs."""
        self.assertNotEqual(self.copy_quiz(self.quiz, question=str(self.quiz.question).lower()), self.quiz)

    def test_equal_when_answers_have_different_case(self):
        """Test that quizzes are equal if only the case of the answers differs."""
        answers = [str(answer).lower() for answer in self.quiz.answers]
        self.assertEqual(self.copy_quiz(self.quiz, answers=answers), self.quiz)
