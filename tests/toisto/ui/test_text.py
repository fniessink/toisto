"""Unit tests for the output."""

from unittest import TestCase

from toisto.model.language.concept_factory import create_concept
from toisto.model.language.label import Label
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.ui.dictionary import DICTIONARY_URL, linkify
from toisto.ui.text import feedback_correct, feedback_incorrect, instruction

from ...base import ToistoTestCase


class FeedbackTestCase(ToistoTestCase):
    """Unit tests for the feedback function."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.guess = Label("terve")

    def test_correct_first_time(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        concept = create_concept("hi", dict(nl="hoi", fi="terve"))
        quiz = create_quizzes("nl", "fi", concept).by_quiz_type("read").pop()
        feedback_text = feedback_correct(self.guess, quiz)
        self.assertEqual("✅ Correct.\n", feedback_text)

    def test_show_alternative_answer(self):
        """Test that alternative answers are shown."""
        concept = create_concept("hi", dict(nl="hoi", fi=["terve", "hei"]))
        quiz = create_quizzes("nl", "fi", concept).by_quiz_type("read").pop()
        expected_other_answer = linkify(quiz.other_answers(self.guess)[0])
        expected_text = f'✅ Correct.\n[secondary]Another correct answer is "{expected_other_answer}".[/secondary]\n'
        self.assertEqual(expected_text, feedback_correct(self.guess, quiz))

    def test_show_alternative_answers(self):
        """Test that alternative answers are shown."""
        concept = create_concept("hi", dict(nl="hoi", fi=["terve", "hei", "hei hei"]))
        quiz = create_quizzes("nl", "fi", concept).by_quiz_type("read").pop()
        other_answers = [f'"{linkify(answer)}"' for answer in quiz.other_answers(self.guess)]
        expected_text = f'✅ Correct.\n[secondary]Other correct answers are {", ".join(other_answers)}.[/secondary]\n'
        self.assertEqual(expected_text, feedback_correct(self.guess, quiz))

    def test_show_feedback_on_incorrect_guess(self):
        """Test that the correct feedback is given when the user guesses incorrectly."""
        concept = create_concept("hi", dict(nl="hoi", fi="terve"))
        quiz = create_quizzes("fi", "nl", concept).by_quiz_type("listen").pop()
        expected_text = (
            f'❌ Incorrect. The correct answer is "[inserted]{linkify("terve")}[/inserted]".\n'
            f'[secondary]Meaning "{linkify("hoi")}".[/secondary]\n'
        )
        self.assertEqual(expected_text, feedback_incorrect("", quiz))

    def test_show_alternative_answers_on_incorrect_guess(self):
        """Test that alternative answers are also given when the user guesses incorrectly."""
        concept = create_concept("hi", dict(nl="hoi", fi=["terve", "hei"]))
        quiz = create_quizzes("nl", "fi", concept).by_quiz_type("read").pop()
        expected_text = (
            f'❌ Incorrect. The correct answer is "[inserted]{linkify("terve")}[/inserted]".\n'
            f'[secondary]Another correct answer is "{linkify("hei")}".[/secondary]\n'
        )
        self.assertEqual(expected_text, feedback_incorrect("", quiz))

    def test_show_feedback_on_question_mark(self):
        """Test that the correct feedback is given when the user doesn't know the answer."""
        concept = create_concept("hi", dict(nl="hoi", fi="terve"))
        quiz = create_quizzes("fi", "nl", concept).by_quiz_type("listen").pop()
        expected_text = (
            f'The correct answer is "{linkify("terve")}".\n[secondary]Meaning "{linkify("hoi")}".[/secondary]\n'
        )
        self.assertEqual(expected_text, feedback_incorrect("?", quiz))

    def test_instruction(self):
        """Test that the quiz instruction is correctly formatted."""
        concept = create_concept("hi", dict(nl="hoi", fi="terve"))
        quiz = create_quizzes("fi", "nl", concept).by_quiz_type("write").pop()
        self.assertEqual("[quiz]Translate into Finnish:[/quiz]", instruction(quiz))

    def test_instruction_multiple_quiz_types(self):
        """Test that the quiz instruction is correctly formatted for multiple quiz types."""
        concept = create_concept(
            "eat",
            {"first person": dict(nl="ik eet"), "third person": dict(female=dict(nl="zij eet"))},
        )
        quiz = create_quizzes("nl", "nl", concept).by_quiz_type("give third person").by_quiz_type("feminize").pop()
        expected_text = "[quiz]Give the [underline]third person female[/underline] in Dutch:[/quiz]"
        self.assertEqual(expected_text, instruction(quiz))

    def test_post_quiz_note(self):
        """Test that the post quiz note is formatted correctly."""
        concept = create_concept("hi", dict(fi="moi;;Moi is an informal greeting"))
        quiz = create_quizzes("fi", "fi", concept).by_quiz_type("listen").pop()
        self.assertEqual(
            "[secondary]Note: Moi is an informal greeting.[/secondary]",
            feedback_correct("moi", quiz).split("\n")[-2],
        )

    def test_multiple_post_quiz_notes(self):
        """Test that multiple post quiz notes are formatted correctly."""
        concept = create_concept("hi", dict(fi="moi;;Moi is an informal greeting;'Moi moi' means goodbye"))
        quiz = create_quizzes("fi", "fi", concept).by_quiz_type("listen").pop()
        self.assertIn(
            "[secondary]Notes:\n- Moi is an informal greeting.\n- 'Moi moi' means goodbye.\n[/secondary]",
            feedback_correct("moi", quiz),
        )

    def test_post_quiz_note_on_incorrect_answer(self):
        """Test that the post quiz note is formatted correctly."""
        concept = create_concept("hi", dict(fi="moi;;Moi is an informal greeting"))
        quiz = create_quizzes("fi", "fi", concept).by_quiz_type("listen").pop()
        self.assertEqual(
            "[secondary]Note: Moi is an informal greeting.[/secondary]",
            feedback_incorrect("toi", quiz).split("\n")[-2],
        )

    def test_post_quiz_note_on_skip_to_answer(self):
        """Test that the post quiz note is formatted correctly."""
        concept = create_concept("hi", dict(fi="moi;;Moi is an informal greeting"))
        quiz = create_quizzes("fi", "fi", concept).by_quiz_type("listen").pop()
        self.assertEqual(
            "[secondary]Note: Moi is an informal greeting.[/secondary]",
            feedback_incorrect("?", quiz).split("\n")[-2],
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
