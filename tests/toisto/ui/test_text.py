"""Unit tests for the output."""

from unittest import TestCase

from toisto.model.language import Language
from toisto.model.language.label import Label
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.persistence.spelling_alternatives import load_spelling_alternatives
from toisto.ui.dictionary import DICTIONARY_URL, linkify
from toisto.ui.style import INSERTED, QUIZ, SECONDARY
from toisto.ui.text import CORRECT, INCORRECT, feedback_correct, feedback_incorrect, instruction

from ...base import ToistoTestCase


class FeedbackTestCase(ToistoTestCase):
    """Unit tests for the feedback function."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        super().setUp()
        load_spelling_alternatives(Language(self.fi), Language(self.nl))
        self.guess = Label(Language(self.fi), "terve")

    def test_correct_first_time(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        concept = self.create_concept("hi", dict(nl="hoi", fi="terve"))
        quiz = create_quizzes(self.nl, self.fi, concept).by_quiz_type("read").pop()
        feedback_text = feedback_correct(self.guess, quiz)
        self.assertEqual(CORRECT, feedback_text)

    def test_show_alternative_answer(self):
        """Test that alternative answers are shown."""
        concept = self.create_concept("hi", dict(nl="hoi", fi=["terve", "hei"]))
        quiz = create_quizzes(self.nl, self.fi, concept).by_quiz_type("read").pop()
        expected_other_answer = linkify(quiz.other_answers(self.guess)[0])
        expected_text = f'{CORRECT}[{SECONDARY}]Another correct answer is "{expected_other_answer}".[/{SECONDARY}]\n'
        self.assertEqual(expected_text, feedback_correct(self.guess, quiz))

    def test_show_alternative_answers(self):
        """Test that alternative answers are shown."""
        concept = self.create_concept("hi", dict(nl="hoi", fi=["terve", "hei", "hei hei"]))
        quiz = create_quizzes(self.nl, self.fi, concept).by_quiz_type("read").pop()
        other_answers = [f'"{linkify(answer)}"' for answer in quiz.other_answers(self.guess)]
        expected_text = f'{CORRECT}[{SECONDARY}]Other correct answers are {", ".join(other_answers)}.[/{SECONDARY}]\n'
        self.assertEqual(expected_text, feedback_correct(self.guess, quiz))

    def test_show_feedback_on_incorrect_guess(self):
        """Test that the correct feedback is given when the user guesses incorrectly."""
        concept = self.create_concept("hi", dict(nl="hoi", fi="terve"))
        quiz = create_quizzes(self.fi, self.nl, concept).by_quiz_type("dictate").pop()
        expected_text = (
            f'{INCORRECT}The correct answer is "[{INSERTED}]{linkify("terve")}[/{INSERTED}]".\n'
            f'[{SECONDARY}]Meaning "{linkify("hoi")}".[/{SECONDARY}]\n'
        )
        self.assertEqual(expected_text, feedback_incorrect(Label(self.fi, "incorrect"), quiz))

    def test_show_alternative_answers_on_incorrect_guess(self):
        """Test that alternative answers are also given when the user guesses incorrectly."""
        concept = self.create_concept("hi", dict(nl="hoi", fi=["terve", "hei"]))
        quiz = create_quizzes(self.nl, self.fi, concept).by_quiz_type("read").pop()
        expected_text = (
            f'{INCORRECT}The correct answer is "[{INSERTED}]{linkify("terve")}[/{INSERTED}]".\n'
            f'[{SECONDARY}]Another correct answer is "{linkify("hei")}".[/{SECONDARY}]\n'
        )
        self.assertEqual(expected_text, feedback_incorrect(Label(self.fi, "incorrect"), quiz))

    def test_do_not_show_generated_alternative_answers_on_incorrect_guess(self):
        """Test that generated alternative answers are not shown when the user guesses incorrectly."""
        concept = self.create_concept("house", dict(nl="het huis", fi=["talo"]))
        quiz = create_quizzes(self.fi, self.nl, concept).by_quiz_type("read").pop()
        expected_text = f'{INCORRECT}The correct answer is "[{INSERTED}]{linkify("het huis")}[/{INSERTED}]".\n'
        self.assertEqual(expected_text, feedback_incorrect(Label(self.nl, "incorrect"), quiz))

    def test_do_not_show_generated_alternative_answers_on_question_mark(self):
        """Test that generated alternative answers are not shown when the user enters a question mark."""
        concept = self.create_concept("house", dict(nl="het huis", fi=["talo"]))
        quiz = create_quizzes(self.fi, self.nl, concept).by_quiz_type("read").pop()
        expected_text = f'The correct answer is "{linkify("het huis")}".\n'
        self.assertEqual(expected_text, feedback_incorrect(Label(self.nl, "?"), quiz))

    def test_show_feedback_on_question_mark(self):
        """Test that the correct feedback is given when the user doesn't know the answer."""
        concept = self.create_concept("hi", dict(nl="hoi", fi="terve"))
        quiz = create_quizzes(self.fi, self.nl, concept).by_quiz_type("dictate").pop()
        expected_text = (
            f'The correct answer is "{linkify("terve")}".\n[{SECONDARY}]Meaning "{linkify("hoi")}".[/{SECONDARY}]\n'
        )
        self.assertEqual(expected_text, feedback_incorrect(Label(self.fi, "?"), quiz))

    def test_show_feedback_on_question_mark_with_multiple_answers(self):
        """Test that the correct feedback is given when the user doesn't know the answer."""
        concept = self.create_concept("hi", dict(nl="hoi", fi=["terve", "hei"]))
        quiz = create_quizzes(self.nl, self.fi, concept).by_quiz_type("read").pop()
        expected_text = (
            'The correct answers are "[link=https://en.wiktionary.org/wiki/terve]terve[/link]", '
            '"[link=https://en.wiktionary.org/wiki/hei]hei[/link]".\n'
        )
        self.assertEqual(expected_text, feedback_incorrect(Label(self.fi, "?"), quiz))

    def test_instruction(self):
        """Test that the quiz instruction is correctly formatted."""
        concept = self.create_concept("hi", dict(nl="hoi", fi="terve"))
        quiz = create_quizzes(self.fi, self.nl, concept).by_quiz_type("write").pop()
        self.assertEqual(f"[{QUIZ}]Translate into Finnish:[/{QUIZ}]", instruction(quiz))

    def test_instruction_multiple_quiz_types(self):
        """Test that the quiz instruction is correctly formatted for multiple quiz types."""
        concept = self.create_concept(
            "eat",
            {"first person": dict(nl="ik eet"), "third person": dict(female=dict(nl="zij eet"))},
        )
        quizzes = create_quizzes(self.nl, self.nl, concept)
        quiz = quizzes.by_quiz_type("give third person").by_quiz_type("feminize").pop()
        expected_text = f"[{QUIZ}]Give the [underline]third person female[/underline] in Dutch:[/{QUIZ}]"
        self.assertEqual(expected_text, instruction(quiz))

    def test_post_quiz_note(self):
        """Test that the post quiz note is formatted correctly."""
        concept = self.create_concept("hi", dict(nl="hoi;;Hoi is an informal greeting"))
        quiz = create_quizzes(self.nl, self.nl, concept).by_quiz_type("dictate").pop()
        self.assertEqual(
            f"[{SECONDARY}]Note: Hoi is an informal greeting.[/{SECONDARY}]",
            feedback_correct(Label(self.nl, "hoi"), quiz).split("\n")[-2],
        )

    def test_multiple_post_quiz_notes(self):
        """Test that multiple post quiz notes are formatted correctly."""
        concept = self.create_concept("hi", dict(fi="moi;;Moi is an informal greeting;'Moi moi' means goodbye"))
        quiz = create_quizzes(self.fi, self.fi, concept).by_quiz_type("dictate").pop()
        self.assertIn(
            f"[{SECONDARY}]Notes:\n- Moi is an informal greeting.\n- 'Moi moi' means goodbye.\n[/{SECONDARY}]",
            feedback_correct(Label(self.fi, "moi"), quiz),
        )

    def test_post_quiz_note_on_incorrect_answer(self):
        """Test that the post quiz note is formatted correctly."""
        concept = self.create_concept("hi", dict(fi="moi;;Moi is an informal greeting"))
        quiz = create_quizzes(self.fi, self.fi, concept).by_quiz_type("dictate").pop()
        self.assertEqual(
            f"[{SECONDARY}]Note: Moi is an informal greeting.[/{SECONDARY}]",
            feedback_incorrect(Label(self.fi, "toi"), quiz).split("\n")[-2],
        )

    def test_post_quiz_note_on_skip_to_answer(self):
        """Test that the post quiz note is formatted correctly."""
        concept = self.create_concept("hi", dict(fi="moi;;Moi is an informal greeting"))
        quiz = create_quizzes(self.fi, self.fi, concept).by_quiz_type("dictate").pop()
        self.assertEqual(
            f"[{SECONDARY}]Note: Moi is an informal greeting.[/{SECONDARY}]",
            feedback_incorrect(Label(self.fi, "?"), quiz).split("\n")[-2],
        )


class LinkifyTest(TestCase):
    """Unit tests for the linkify method."""

    def test_linkify(self):
        """Test the linkify method."""
        self.assertEqual(f"[link={DICTIONARY_URL}/test]Test[/link]", linkify("Test"))

    def test_linkify_multiple_words(self):
        """Test the linkify method."""
        expected_text = f"[link={DICTIONARY_URL}/test]Test[/link] [link={DICTIONARY_URL}/words]words[/link]"
        self.assertEqual(expected_text, linkify("Test words"))

    def test_punctuation(self):
        """Test that punctuation is not linked."""
        self.assertEqual(f"[link={DICTIONARY_URL}/test]Test[/link].", linkify("Test."))
