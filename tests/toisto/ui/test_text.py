"""Unit tests for the output."""

from unittest import TestCase

from toisto.model.language import FI, NL
from toisto.model.language.label import Label
from toisto.model.quiz.evaluation import Evaluation
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import DICTATE, FEMININE, READ, WRITE
from toisto.persistence.spelling_alternatives import load_spelling_alternatives
from toisto.ui.dictionary import DICTIONARY_URL, linkified
from toisto.ui.text import Feedback, enumerated, instruction

from ...base import FI_NL, NL_FI, ToistoTestCase


class FeedbackTestCase(ToistoTestCase):
    """Unit tests for the feedback function."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        super().setUp()
        load_spelling_alternatives(FI_NL)
        self.guess = Label(FI_NL.target, "terve")

    def test_correct_first_time(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        concept = self.create_concept(
            "hi", labels=[{"label": "hoi", "language": NL}, {"label": "terve", "language": FI}]
        )
        quiz = create_quizzes(NL_FI, (READ,), concept).pop()
        feedback = Feedback(quiz, NL_FI)
        self.assertEqual(Feedback.CORRECT, feedback(Evaluation.CORRECT, self.guess))

    def test_show_colloquial_language(self):
        """Test that the colloquial language, that is only spoken, is shown."""
        concept = self.create_concept(
            "thanks",
            labels=[
                {"label": "dank", "language": NL},
                {"label": "kiitos", "language": FI},
                {"label": "kiitti", "language": FI, "colloquial": True},
            ],
        )
        colloquial = "[secondary]The colloquial Finnish spoken was 'kiitti'.[/secondary]\n"
        meaning = f"[secondary]Meaning '{linkified('dank')}'.[/secondary]\n"
        answer = f"The correct answer is '[inserted]{linkified('kiitos')}[/inserted]'.\n"
        expected_feedback_correct = Feedback.CORRECT + colloquial + meaning
        expected_feedback_incorrect = Feedback.INCORRECT + answer + colloquial + meaning
        expected_feedback_on_skip = f"The correct answer is '{linkified('kiitos')}'.\n" + colloquial + meaning
        for quiz in create_quizzes(FI_NL, (DICTATE,), concept):
            feedback = Feedback(quiz, FI_NL)
            if quiz.question.colloquial:
                self.assertEqual(expected_feedback_correct, feedback(Evaluation.CORRECT, Label(FI, "kiitos")))
                self.assertEqual(expected_feedback_incorrect, feedback(Evaluation.INCORRECT, Label(FI, "hei")))
                self.assertEqual(expected_feedback_on_skip, feedback(Evaluation.SKIPPED))

    def test_show_alternative_answer(self):
        """Test that alternative answers are shown."""
        concept = self.create_concept(
            "hi",
            labels=[
                {"label": "hoi", "language": NL},
                {"label": "terve", "language": FI},
                {"label": "hei", "language": FI},
            ],
        )
        quiz = create_quizzes(NL_FI, (READ,), concept).pop()
        expected_other_answer = linkified(str(quiz.other_answers(self.guess)[0]))
        expected_text = (
            f"{Feedback.CORRECT}[secondary]Another correct answer is '{expected_other_answer}'.[/secondary]\n"
        )
        feedback = Feedback(quiz, NL_FI)
        self.assertEqual(expected_text, feedback(Evaluation.CORRECT, self.guess))

    def test_show_alternative_answers(self):
        """Test that alternative answers are shown."""
        concept = self.create_concept(
            "hi",
            labels=[
                {"label": "hoi", "language": NL},
                {"label": "terve", "language": FI},
                {"label": "hei", "language": FI},
                {"label": "hei hei", "language": FI},
            ],
        )
        quiz = create_quizzes(NL_FI, (READ,), concept).pop()
        other_answers = enumerated(*[f"'{linkified(str(answer))}'" for answer in quiz.other_answers(self.guess)])
        expected_text = f"{Feedback.CORRECT}[secondary]Other correct answers are {other_answers}.[/secondary]\n"
        feedback = Feedback(quiz, NL_FI)
        self.assertEqual(expected_text, feedback(Evaluation.CORRECT, self.guess))

    def test_show_feedback_on_incorrect_guess(self):
        """Test that the correct feedback is given when the user guesses incorrectly."""
        concept = self.create_concept(
            "hi", labels=[{"label": "hoi", "language": NL}, {"label": "terve", "language": FI}]
        )
        quiz = create_quizzes(FI_NL, (DICTATE,), concept).pop()
        expected_text = (
            f"{Feedback.INCORRECT}The correct answer is '[inserted]{linkified('terve')}[/inserted]'.\n"
            f"[secondary]Meaning '{linkified('hoi')}'.[/secondary]\n"
        )
        feedback = Feedback(quiz, FI_NL)
        self.assertEqual(expected_text, feedback(Evaluation.INCORRECT, Label(FI, "incorrect")))

    def test_show_alternative_answers_on_incorrect_guess(self):
        """Test that alternative answers are also given when the user guesses incorrectly."""
        concept = self.create_concept(
            "hi",
            labels=[
                {"label": "hoi", "language": NL},
                {"label": "terve", "language": FI},
                {"label": "hei", "language": FI},
            ],
        )
        quiz = create_quizzes(NL_FI, (READ,), concept).pop()
        expected_text = (
            f"{Feedback.INCORRECT}The correct answer is '[inserted]{linkified('terve')}[/inserted]'.\n"
            f"[secondary]Another correct answer is '{linkified('hei')}'.[/secondary]\n"
        )
        feedback = Feedback(quiz, NL_FI)
        self.assertEqual(expected_text, feedback(Evaluation.INCORRECT, Label(FI, "incorrect")))

    def test_do_not_show_generated_alternative_answers_on_incorrect_guess(self):
        """Test that generated alternative answers are not shown when the user guesses incorrectly."""
        concept = self.create_concept(
            "house", labels=[{"label": "het huis", "language": NL}, {"label": "talo", "language": FI}]
        )
        quiz = create_quizzes(FI_NL, (READ,), concept).pop()
        expected_text = f"{Feedback.INCORRECT}The correct answer is '[inserted]{linkified('het huis')}[/inserted]'.\n"
        feedback = Feedback(quiz, FI_NL)
        self.assertEqual(expected_text, feedback(Evaluation.INCORRECT, Label(NL, "incorrect")))

    def test_do_not_show_generated_alternative_answers_on_question_mark(self):
        """Test that generated alternative answers are not shown when the user enters a question mark."""
        concept = self.create_concept(
            "house", labels=[{"label": "het huis", "language": NL}, {"label": "talo", "language": FI}]
        )
        quiz = create_quizzes(FI_NL, (READ,), concept).pop()
        expected_text = f"The correct answer is '{linkified('het huis')}'.\n"
        feedback = Feedback(quiz, FI_NL)
        self.assertEqual(expected_text, feedback(Evaluation.SKIPPED))

    def test_show_feedback_on_question_mark(self):
        """Test that the correct feedback is given when the user doesn't know the answer."""
        concept = self.create_concept(
            "hi", labels=[{"label": "hoi", "language": NL}, {"label": "terve", "language": FI}]
        )
        quiz = create_quizzes(FI_NL, (DICTATE,), concept).pop()
        expected_text = (
            f"The correct answer is '{linkified('terve')}'.\n[secondary]Meaning '{linkified('hoi')}'.[/secondary]\n"
        )
        feedback = Feedback(quiz, FI_NL)
        self.assertEqual(expected_text, feedback(Evaluation.SKIPPED))

    def test_show_feedback_on_question_mark_with_multiple_answers(self):
        """Test that the correct feedback is given when the user doesn't know the answer."""
        concept = self.create_concept(
            "hi",
            labels=[
                {"label": "hoi", "language": NL},
                {"label": "terve", "language": FI},
                {"label": "hei", "language": FI},
            ],
        )
        quiz = create_quizzes(NL_FI, (READ,), concept).pop()
        expected_text = (
            "The correct answers are '[link=https://en.wiktionary.org/wiki/terve]terve[/link]' and "
            "'[link=https://en.wiktionary.org/wiki/hei]hei[/link]'.\n"
        )
        feedback = Feedback(quiz, NL_FI)
        self.assertEqual(expected_text, feedback(Evaluation.SKIPPED))

    def test_instruction(self):
        """Test that the quiz instruction is correctly formatted."""
        concept = self.create_concept(
            "hi",
            labels=[
                {"label": "hoi", "language": NL},
                {"label": "terve", "language": FI},
                {"label": "hei", "language": FI},
            ],
        )
        quiz = create_quizzes(FI_NL, (WRITE,), concept).pop()
        self.assertEqual("[quiz]Translate into Finnish:[/quiz]", instruction(quiz))

    def test_instruction_multiple_quiz_types(self):
        """Test that the quiz instruction is correctly formatted for multiple quiz types."""
        concept = self.create_concept(
            "eat",
            labels=[{"label": {"first person": "ik eet", "third person": {"feminine": "zij eet"}}, "language": NL}],
        )
        quiz = create_quizzes(NL_FI, (FEMININE,), concept).pop()
        expected_text = "[quiz]Give the [underline]third person feminine[/underline] in Dutch:[/quiz]"
        self.assertEqual(expected_text, instruction(quiz))

    def test_post_quiz_note(self):
        """Test that the post quiz note is formatted correctly."""
        concept = self.create_concept(
            "hi", labels=[{"label": "hoi", "language": NL, "note": "'Hoi' is an informal greeting"}]
        )
        quiz = create_quizzes(NL_FI, (DICTATE,), concept).pop()
        feedback = Feedback(quiz, NL_FI)
        self.assertEqual(
            "[secondary]Note: 'Hoi' is an informal greeting.[/secondary]",
            feedback(Evaluation.CORRECT, Label(NL, "hoi")).split("\n")[-2],
        )

    def test_multiple_post_quiz_notes(self):
        """Test that multiple post quiz notes are formatted correctly."""
        concept = self.create_concept(
            "hi",
            labels=[
                {"label": "moi", "language": FI, "note": ["Moi is an informal greeting", "'Moi moi' means goodbye"]}
            ],
        )
        quiz = create_quizzes(FI_NL, (DICTATE,), concept).pop()
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(
            "[secondary]Notes:\n- Moi is an informal greeting.\n- 'Moi moi' means goodbye.[/secondary]\n",
            feedback(Evaluation.CORRECT, Label(FI, "moi")),
        )

    def test_post_quiz_note_on_incorrect_answer(self):
        """Test that the post quiz note is formatted correctly."""
        concept = self.create_concept(
            "hi", labels=[{"label": "moi", "language": FI, "note": "'Moi' is an informal greeting"}]
        )
        quiz = create_quizzes(FI_NL, (DICTATE,), concept).pop()
        feedback = Feedback(quiz, FI_NL)
        self.assertEqual(
            "[secondary]Note: 'Moi' is an informal greeting.[/secondary]",
            feedback(Evaluation.INCORRECT, Label(FI, "toi")).split("\n")[-2],
        )

    def test_post_quiz_note_on_skip_to_answer(self):
        """Test that the post quiz note is formatted correctly."""
        concept = self.create_concept(
            "hi", labels=[{"label": "moi", "language": FI, "note": "'Moi' is an informal greeting"}]
        )
        quiz = create_quizzes(FI_NL, (DICTATE,), concept).pop()
        feedback = Feedback(quiz, FI_NL)
        self.assertEqual(
            "[secondary]Note: 'Moi' is an informal greeting.[/secondary]",
            feedback(Evaluation.SKIPPED, Label(FI, "?")).split("\n")[-2],
        )

    def test_post_quiz_example_with_spelling_alternatives(self):
        """Test that the post quiz example is formatted correctly when the example has spelling alternatives."""
        hi = self.create_concept(
            "hi", {"example": "hi alice"}, labels=[{"label": "hoi", "language": NL}, {"label": "terve", "language": FI}]
        )
        self.create_concept(
            "hi alice",
            labels=[{"label": ["Moi Alice!", "Hei Alice!"], "language": FI}, {"label": "Hoi Alice!", "language": NL}],
        )
        quiz = create_quizzes(FI_NL, (READ,), hi).pop()
        feedback = Feedback(quiz, FI_NL)
        self.assertEqual(
            Feedback.CORRECT + "[secondary]Example: 'Moi Alice!' meaning 'Hoi Alice!'[/secondary]\n",
            feedback(Evaluation.CORRECT, Label(NL, "hoi")),
        )

    def test_post_quiz_example_with_write_quiz(self):
        """Test that the post quiz example is in the right language when the quiz type is write."""
        hi = self.create_concept(
            "hi", {"example": "hi alice"}, labels=[{"label": "hoi", "language": NL}, {"label": "terve", "language": FI}]
        )
        self.create_concept(
            "hi alice", labels=[{"label": "Terve Alice!", "language": FI}, {"label": "Hoi Alice!", "language": NL}]
        )
        quiz = create_quizzes(FI_NL, (WRITE,), hi).pop()
        feedback = Feedback(quiz, FI_NL)
        self.assertEqual(
            Feedback.CORRECT + "[secondary]Example: 'Terve Alice!' meaning 'Hoi Alice!'[/secondary]\n",
            feedback(Evaluation.CORRECT, self.guess),
        )

    def test_post_quiz_example_with_multiple_meanings(self):
        """Test that the post quiz example is not repeated if an example has multiple meanings."""
        hi = self.create_concept(
            "hi", {"example": "hi alice"}, labels=[{"label": "hoi", "language": NL}, {"label": "terve", "language": FI}]
        )
        self.create_concept(
            "hi alice",
            labels=[
                {"label": "Terve Alice!", "language": FI},
                {"label": "Hoi Alice!", "language": NL},
                {"label": "Hallo Alice!", "language": NL},
            ],
        )
        quiz = create_quizzes(FI_NL, (WRITE,), hi).pop()
        feedback = Feedback(quiz, FI_NL)
        self.assertEqual(
            Feedback.CORRECT
            + "[secondary]Example: 'Terve Alice!' meaning 'Hoi Alice!' and 'Hallo Alice!'[/secondary]\n",
            feedback(Evaluation.CORRECT, self.guess),
        )

    def test_post_quiz_example_with_colloquial_labels(self):
        """Test that the star is removed from colloquial labels."""
        hi = self.create_concept(
            "hi", {"example": "hi alice"}, labels=[{"label": "hoi", "language": NL}, {"label": "terve", "language": FI}]
        )
        self.create_concept(
            "hi alice",
            labels=[
                {"label": "Terve Alice!", "language": FI},
                {"label": "Moi Alice!", "language": FI, "colloquial": True},
                {"label": "Hallo Alice!", "language": NL},
                {"label": "Hoi Alice!", "language": NL, "colloquial": True},
            ],
        )
        quiz = create_quizzes(FI_NL, (WRITE,), hi).pop()
        feedback = Feedback(quiz, FI_NL)
        self.assertEqual(
            Feedback.CORRECT
            + "[secondary]Examples:\n"
            + "- 'Terve Alice!' meaning 'Hallo Alice!' and 'Hoi Alice!' (colloquial).\n"
            + "- 'Moi Alice!' (colloquial) meaning 'Hallo Alice!' and 'Hoi Alice!' (colloquial).[/secondary]\n",
            feedback(Evaluation.CORRECT, self.guess),
        )

    def test_post_quiz_example_with_synonyms(self):
        """Test that the post quiz example is for the correct synonym."""
        near = self.create_concept(
            "near",
            {"example": "it is near"},
            labels=[
                {"label": "lähellä", "language": FI},
                {"label": "dichtbij", "language": NL},
                {"label": "in de buurt", "language": NL},
            ],
        )
        self.create_concept(
            "it is near",
            labels=[
                {"label": "Se on lähellä.", "language": FI},
                {"label": "Het is dichtbij.", "language": NL},
                {"label": "Het is in de buurt.", "language": NL},
            ],
        )
        quiz = create_quizzes(FI_NL, (READ,), near).pop()
        feedback = Feedback(quiz, FI_NL)
        self.assertEqual(
            Feedback.CORRECT + "[secondary]Another correct answer is "
            "'[link=https://en.wiktionary.org/wiki/dichtbij]dichtbij[/link]'.[/secondary]\n"
            "[secondary]Example: 'Se on lähellä.' meaning 'Het is dichtbij.' and 'Het is in de buurt.'[/secondary]\n",
            feedback(Evaluation.CORRECT, Label(NL, "in de buurt")),
        )


class LinkifyTest(TestCase):
    """Unit tests for the linkify method."""

    def test_linkify(self):
        """Test the linkify method."""
        self.assertEqual(f"[link={DICTIONARY_URL}/test]Test[/link]", linkified("Test"))

    def test_linkify_multiple_words(self):
        """Test the linkify method."""
        expected_text = f"[link={DICTIONARY_URL}/test]Test[/link] [link={DICTIONARY_URL}/words]words[/link]"
        self.assertEqual(expected_text, linkified("Test words"))

    def test_punctuation(self):
        """Test that punctuation is not linked."""
        self.assertEqual(f"[link={DICTIONARY_URL}/test]Test[/link].", linkified("Test."))


class EnumeratedTest(TestCase):
    """Unit tests for the enumerated method."""

    def test_no_arguments(self):
        """Test the enumerated method without arguments."""
        self.assertEqual("", enumerated())

    def test_empty_string(self):
        """Test the enumerated method with an empty string."""
        self.assertEqual("", enumerated(""))

    def test_one_word(self):
        """Test the enumerated method with one word."""
        self.assertEqual("foo", enumerated("foo"))

    def test_two_words(self):
        """Test the enumerated method with two words."""
        self.assertEqual("foo and bar", enumerated("foo", "bar"))

    def test_three_words(self):
        """Test the enumerated method with three words."""
        self.assertEqual("foo, bar, and baz", enumerated("foo", "bar", "baz"))
