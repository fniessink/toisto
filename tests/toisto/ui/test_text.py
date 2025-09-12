"""Unit tests for the output."""

from datetime import datetime, timedelta

from toisto.model.language import FI, NL
from toisto.model.language.concept import ConceptId
from toisto.model.language.label import Label
from toisto.model.quiz.evaluation import Evaluation
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import DICTATE, FEMININE, INTERPRET, READ, WRITE
from toisto.model.quiz.retention import Retention
from toisto.ui.dictionary import linkified
from toisto.ui.format import enumerated
from toisto.ui.text import Feedback, instruction

from ...base import FI_NL, NL_FI, ToistoTestCase


class InstructionTest(ToistoTestCase):
    """Unit tests for the instruction."""

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
        expected_text = "[quiz]Give the [underline]feminine third person[/underline] in Dutch:[/quiz]"
        self.assertEqual(expected_text, instruction(quiz))


GUESS = Label(FI_NL.target, "terve")


class FeedbackTest(ToistoTestCase):
    """Unit tests for the feedback function."""

    def test_correct_first_time(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        concept = self.create_concept(
            "hi", labels=[{"label": "hoi", "language": NL}, {"label": "terve", "language": FI}]
        )
        quiz = create_quizzes(NL_FI, (READ,), concept).pop()
        feedback = Feedback(quiz, NL_FI)
        self.assertIn(Feedback.CORRECT, feedback.text(Evaluation.CORRECT, GUESS, Retention()))

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
                self.assertIn(
                    expected_feedback_correct, feedback.text(Evaluation.CORRECT, Label(FI, "kiitos"), Retention())
                )
                self.assertIn(
                    expected_feedback_incorrect, feedback.text(Evaluation.INCORRECT, Label(FI, "hei"), Retention())
                )
                self.assertIn(expected_feedback_on_skip, feedback.text(Evaluation.SKIPPED, Label(FI, "?"), Retention()))

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
        expected_other_answer = linkified(str(quiz.other_answers(GUESS)[0]))
        expected_text = (
            f"{Feedback.CORRECT}[secondary]Another correct answer is '{expected_other_answer}'.[/secondary]\n"
        )
        feedback = Feedback(quiz, NL_FI)
        self.assertIn(expected_text, feedback.text(Evaluation.CORRECT, GUESS, Retention()))

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
        other_answers = enumerated(*[f"'{linkified(str(answer))}'" for answer in quiz.other_answers(GUESS)])
        expected_text = f"{Feedback.CORRECT}[secondary]Other correct answers are {other_answers}.[/secondary]\n"
        feedback = Feedback(quiz, NL_FI)
        self.assertIn(expected_text, feedback.text(Evaluation.CORRECT, GUESS, Retention()))

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
        self.assertIn(expected_text, feedback.text(Evaluation.INCORRECT, Label(FI, "incorrect"), Retention()))

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
        self.assertIn(expected_text, feedback.text(Evaluation.INCORRECT, Label(FI, "incorrect"), Retention()))

    def test_do_not_show_generated_alternative_answers_on_incorrect_guess(self):
        """Test that generated alternative answers are not shown when the user guesses incorrectly."""
        concept = self.create_concept(
            "house", labels=[{"label": "het huis", "language": NL}, {"label": "talo", "language": FI}]
        )
        quiz = create_quizzes(FI_NL, (READ,), concept).pop()
        expected_text = f"{Feedback.INCORRECT}The correct answer is '[inserted]{linkified('het huis')}[/inserted]'.\n"
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(expected_text, feedback.text(Evaluation.INCORRECT, Label(NL, "incorrect"), Retention()))

    def test_do_not_show_generated_alternative_answers_on_question_mark(self):
        """Test that generated alternative answers are not shown when the user enters a question mark."""
        concept = self.create_concept(
            "house", labels=[{"label": "het huis", "language": NL}, {"label": "talo", "language": FI}]
        )
        quiz = create_quizzes(FI_NL, (READ,), concept).pop()
        expected_text = f"The correct answer is '{linkified('het huis')}'.\n"
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(expected_text, feedback.text(Evaluation.SKIPPED, Label(FI, "?"), Retention()))

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
        self.assertIn(expected_text, feedback.text(Evaluation.SKIPPED, Label(FI, "?"), Retention()))

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
        self.assertIn(expected_text, feedback.text(Evaluation.SKIPPED, Label(FI, "?"), Retention()))


class FeedbackNotesTest(ToistoTestCase):
    """Unit tests for the notes given by the feedback function."""

    def test_note(self):
        """Test that the post quiz note is formatted correctly."""
        concept = self.create_concept(
            "hi", labels=[{"label": "hoi", "language": NL, "note": "'Hoi' is an informal greeting"}]
        )
        quiz = create_quizzes(NL_FI, (DICTATE,), concept).pop()
        feedback = Feedback(quiz, NL_FI)
        self.assertIn(
            "[secondary]Note: 'Hoi' is an informal greeting.[/secondary]",
            feedback.text(Evaluation.CORRECT, Label(NL, "hoi"), Retention()),
        )

    def test_multiple_notes(self):
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
            feedback.text(Evaluation.CORRECT, Label(FI, "moi"), Retention()),
        )

    def test_note_on_incorrect_answer(self):
        """Test that the note is given when the answer is incorrect."""
        concept = self.create_concept(
            "hi", labels=[{"label": "moi", "language": FI, "note": "'Moi' is an informal greeting"}]
        )
        quiz = create_quizzes(FI_NL, (DICTATE,), concept).pop()
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(
            "[secondary]Note: 'Moi' is an informal greeting.[/secondary]",
            feedback.text(Evaluation.INCORRECT, Label(FI, "toi"), Retention()),
        )

    def test_note_on_incorrect_answer_that_has_different_meaning(self):
        """Test that the note is given when the answer is incorrect."""
        self.create_concept(
            "hello",
            labels=[{"label": "terve", "language": FI}, {"label": "hallo", "language": NL}],
        )
        hi = self.create_concept(
            "hi",
            labels=[{"label": "moi", "language": FI}, {"label": "hoi", "language": NL}],
        )
        quiz = create_quizzes(FI_NL, (INTERPRET,), hi).pop()
        feedback = Feedback(quiz, FI_NL)
        feedback.incorrect_guesses = [Label(NL, "hallo")]
        self.assertIn(
            f"[secondary]Note: Your incorrect answer '{linkified('hallo')}' is "
            f"'{linkified('terve')}' in Finnish.[/secondary]",
            feedback.text(Evaluation.CORRECT, Label(NL, "hoi"), Retention()),
        )

    def test_note_on_incorrect_answer_that_has_different_meaning_and_is_spelling_variant(self):
        """Test that the note is given when the answer is incorrect."""
        self.create_concept(
            "house",
            labels=[{"label": "talo", "language": FI}, {"label": ["het huis", "huis"], "language": NL}],
        )
        home = self.create_concept(
            "home",
            labels=[{"label": "koti", "language": FI}, {"label": "thuis", "language": NL}],
        )
        quiz = create_quizzes(FI_NL, (INTERPRET,), home).pop()
        feedback = Feedback(quiz, FI_NL)
        feedback.incorrect_guesses = [Label(NL, "huis")]
        self.assertIn(
            f"[secondary]Note: Your incorrect answer '{linkified('huis')}' is "
            f"'{linkified('talo')}' in Finnish.[/secondary]",
            feedback.text(Evaluation.CORRECT, Label(NL, "thuis"), Retention()),
        )

    def test_note_on_skip_to_answer(self):
        """Test that the note is given when the user skips to the answer."""
        concept = self.create_concept(
            "hi", labels=[{"label": "moi", "language": FI, "note": "'Moi' is an informal greeting"}]
        )
        quiz = create_quizzes(FI_NL, (DICTATE,), concept).pop()
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(
            "[secondary]Note: 'Moi' is an informal greeting.[/secondary]",
            feedback.text(Evaluation.SKIPPED, Label(FI, "?"), Retention()),
        )


class FeedbackRetentionTest(ToistoTestCase):
    """Unit tests for the retention returned by the feedback function."""

    def create_feedback(self) -> Feedback:
        """Create a feedback fixture."""
        concept = self.create_concept(
            "hi", labels=[{"label": "hoi", "language": NL}, {"label": "terve", "language": FI}]
        )
        quiz = create_quizzes(NL_FI, (READ,), concept).pop()
        return Feedback(quiz, NL_FI)

    def test_retention_feedback_correct_after_first_quiz(self):
        """Test the retention feedback after the quiz has been answered correctly on the first try."""
        feedback = self.create_feedback()
        skip_until = datetime.now().astimezone() + timedelta(hours=24)
        self.assertIn(
            "[retention]Correct on the first try! No retention yet. Up next in 24 hours.[/retention]",
            feedback.text(Evaluation.CORRECT, GUESS, Retention(count=1, skip_until=skip_until)),
        )
        self.assertIn(Feedback.CORRECT, feedback.text(Evaluation.CORRECT, GUESS, Retention()))

    def test_retention_feedback_incorrect_after_first_quiz(self):
        """Test the retention feedback after the quiz has been answered incorrectly on the first try."""
        feedback = self.create_feedback()
        self.assertIn(
            "[retention]Quizzed once. No retention yet. Up next soon.[/retention]",
            feedback.text(Evaluation.INCORRECT, GUESS, Retention(count=1)),
        )
        self.assertIn(Feedback.INCORRECT, feedback.text(Evaluation.INCORRECT, GUESS, Retention()))

    def test_retention_feedback_correct_after_second_quiz(self):
        """Test the retention feedback after the quiz has been answered correctly on the second try."""
        feedback = self.create_feedback()
        end = datetime.now().astimezone()
        start = end - timedelta(weeks=4)
        self.assertIn(
            "[retention]Quizzed 2 times. Retention 4 weeks. Up next soon.[/retention]",
            feedback.text(Evaluation.CORRECT, GUESS, Retention(count=2, start=start, end=end)),
        )

    def test_retention_feedback_incorrect_after_second_quiz(self):
        """Test the retention feedback retention after the quiz has been answered incorrectly on the second try."""
        feedback = self.create_feedback()
        self.assertIn(
            "[retention]Quizzed 2 times. No retention yet. Up next soon.[/retention]",
            feedback.text(Evaluation.INCORRECT, GUESS, Retention(count=2)),
        )


class FeedbackMeaningTest(ToistoTestCase):
    """Unit tests for the meaning given by the feedback function."""

    def test_meaning_interpret_quiz_type(self):
        """Test that the correct meaning is given when the quiz is an interpret quiz with singular and plural forms."""
        engineer = self.create_concept(
            "engineer",
            {},
            labels=[
                {"label": {"singular": "ingenieur", "plural": "ingenieurs"}, "language": NL},
                {"label": {"singular": "insinööri", "plural": "insinöörit"}, "language": FI},
            ],
        )
        for quiz in create_quizzes(FI_NL, (INTERPRET,), engineer):
            feedback = Feedback(quiz, FI_NL)
            question = quiz.question
            self.assertIn(
                f"[secondary]Meaning '[link=https://en.wiktionary.org/wiki/{question}]{question}[/link]'.[/secondary]\n",
                feedback.text(Evaluation.CORRECT, Label(NL, "ingenieur"), Retention()),
            )


class FeedbackExampleTest(ToistoTestCase):
    """Unit tests for the examples given by the feedback function."""

    def test_example_with_spelling_alternatives(self):
        """Test that the post quiz example is formatted correctly when the example has spelling alternatives."""
        hi = self.create_concept(
            "hi",
            {"example": ConceptId("hi alice")},
            labels=[{"label": "hoi", "language": NL}, {"label": "terve", "language": FI}],
        )
        self.create_concept(
            "hi alice",
            labels=[{"label": ["Moi Alice!", "Hei Alice!"], "language": FI}, {"label": "Hoi Alice!", "language": NL}],
        )
        quiz = create_quizzes(FI_NL, (READ,), hi).pop()
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(
            Feedback.CORRECT + "[secondary]Example: 'Moi Alice!' meaning 'Hoi Alice!'[/secondary]\n",
            feedback.text(Evaluation.CORRECT, Label(NL, "hoi"), Retention()),
        )

    def test_example_with_write_quiz(self):
        """Test that the post quiz example is in the right language when the quiz type is write."""
        hi = self.create_concept(
            "hi",
            {"example": ConceptId("hi alice")},
            labels=[{"label": "hoi", "language": NL}, {"label": "terve", "language": FI}],
        )
        self.create_concept(
            "hi alice", labels=[{"label": "Terve Alice!", "language": FI}, {"label": "Hoi Alice!", "language": NL}]
        )
        quiz = create_quizzes(FI_NL, (WRITE,), hi).pop()
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(
            Feedback.CORRECT + "[secondary]Example: 'Terve Alice!' meaning 'Hoi Alice!'[/secondary]\n",
            feedback.text(Evaluation.CORRECT, GUESS, Retention()),
        )

    def test_example_with_multiple_meanings(self):
        """Test that the post quiz example is not repeated if an example has multiple meanings."""
        hi = self.create_concept(
            "hi",
            {"example": ConceptId("hi alice")},
            labels=[{"label": "hoi", "language": NL}, {"label": "terve", "language": FI}],
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
        self.assertIn(
            Feedback.CORRECT
            + "[secondary]Example: 'Terve Alice!' meaning 'Hoi Alice!' and 'Hallo Alice!'[/secondary]\n",
            feedback.text(Evaluation.CORRECT, GUESS, Retention()),
        )

    def test_example_with_colloquial_labels(self):
        """Test that the star is removed from colloquial labels."""
        hi = self.create_concept(
            "hi",
            {"example": ConceptId("hi alice")},
            labels=[{"label": "hoi", "language": NL}, {"label": "terve", "language": FI}],
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
        self.assertIn(
            Feedback.CORRECT
            + "[secondary]Examples:\n"
            + "- 'Terve Alice!' meaning 'Hallo Alice!' and 'Hoi Alice!' (colloquial).\n"
            + "- 'Moi Alice!' (colloquial) meaning 'Hallo Alice!' and 'Hoi Alice!' (colloquial).[/secondary]\n",
            feedback.text(Evaluation.CORRECT, GUESS, Retention()),
        )

    def test_example_with_synonyms(self):
        """Test that the post quiz example is for the correct synonym."""
        near = self.create_concept(
            "near",
            {"example": ConceptId("it is near")},
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
        self.assertIn(
            Feedback.CORRECT + "[secondary]Another correct answer is "
            "'[link=https://en.wiktionary.org/wiki/dichtbij]dichtbij[/link]'.[/secondary]\n"
            "[secondary]Example: 'Se on lähellä.' meaning 'Het is dichtbij.' and 'Het is in de buurt.'[/secondary]\n",
            feedback.text(Evaluation.CORRECT, Label(NL, "in de buurt"), Retention()),
        )
