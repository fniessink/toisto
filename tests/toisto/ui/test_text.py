"""Unit tests for the output."""

from configparser import ConfigParser
from datetime import datetime, timedelta
from unittest.mock import patch

from rich.panel import Panel

from toisto.metadata import VERSION
from toisto.model.language import FI, NL
from toisto.model.language.concept import ConceptId
from toisto.model.quiz.evaluation import Evaluation
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import DICTATE, INTERPRET, READ, WRITE
from toisto.model.quiz.retention import Retention
from toisto.persistence.config import default_config
from toisto.ui.dictionary import linkified
from toisto.ui.format import enumerated
from toisto.ui.text import CONFIG_LANGUAGE_TIP, NEWS, WELCOME, Feedback, instruction, show_welcome

from ...base import FI_NL, NL_FI, LabelDict, ToistoTestCase

HEI: LabelDict = {"label": "hei", "language": FI}
HOI: LabelDict = {"label": "hoi", "language": NL}
TERVE: LabelDict = {"label": "terve", "language": FI}


class InstructionTest(ToistoTestCase):
    """Unit tests for the instruction."""

    def test_instruction(self):
        """Test that the quiz instruction is correctly formatted."""
        concept = self.create_concept("hi", labels=[HOI, TERVE, HEI])
        (quiz,) = create_quizzes(FI_NL, (WRITE,), concept)
        self.assertEqual("[quiz]Translate into Finnish:[/quiz]", instruction(quiz))

    def test_instruction_multiple_quiz_types(self):
        """Test that the quiz instruction is correctly formatted for multiple quiz types."""
        concept = self.create_concept(
            "eat",
            labels=[{"label": {"first person": "ik eet", "third person": {"feminine": "zij eet"}}, "language": NL}],
        )
        for quiz in create_quizzes(NL_FI, (), concept):
            if quiz.action == "feminine third person":
                expected_text = "[quiz]Give the [underline]feminine third person[/underline] in Dutch:[/quiz]"
                self.assertEqual(expected_text, instruction(quiz))


GUESS = "terve"


class FeedbackTest(ToistoTestCase):
    """Unit tests for the feedback function."""

    def test_correct_first_time(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        concept = self.create_concept("hi", labels=[HOI, TERVE])
        (quiz,) = create_quizzes(NL_FI, (READ,), concept)
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
        colloquial = f"[colloquial]The colloquial Finnish spoken was '{linkified('kiitti')}'.[/colloquial]\n"
        meaning = f"[meaning]Meaning '{linkified('dank')}'.[/meaning]\n"
        answer = f"The correct answer is '{linkified('kiitos')}'.\n"
        expected_feedback_correct = Feedback.CORRECT + colloquial + meaning
        expected_feedback_incorrect = Feedback.INCORRECT + answer + colloquial + meaning
        expected_feedback_on_skip = f"The correct answer is '{linkified('kiitos')}'.\n" + colloquial + meaning
        for quiz in create_quizzes(FI_NL, (DICTATE,), concept):
            feedback = Feedback(quiz, FI_NL)
            if quiz.question.colloquial:
                self.assertIn(expected_feedback_correct, feedback.text(Evaluation.CORRECT, "kiitos", Retention()))
                self.assertIn(expected_feedback_incorrect, feedback.text(Evaluation.INCORRECT, "hei", Retention()))
                self.assertIn(expected_feedback_on_skip, feedback.text(Evaluation.SKIPPED, "?", Retention()))

    def test_show_alternative_answer(self):
        """Test that alternative answers are shown."""
        concept = self.create_concept("hi", labels=[HOI, TERVE, HEI])
        (quiz,) = create_quizzes(NL_FI, (READ,), concept)
        expected_other_answer = linkified(str(quiz.other_answers(GUESS)[0]))
        expected_text = f"{Feedback.CORRECT}[answer]Another correct answer is '{expected_other_answer}'.[/answer]\n"
        feedback = Feedback(quiz, NL_FI)
        self.assertIn(expected_text, feedback.text(Evaluation.CORRECT, GUESS, Retention()))

    def test_show_alternative_answers(self):
        """Test that alternative answers are shown."""
        concept = self.create_concept("hi", labels=[HOI, TERVE, HEI, {"label": "hei hei", "language": FI}])
        (quiz,) = create_quizzes(NL_FI, (READ,), concept)
        other_answers = enumerated(*[f"'{linkified(str(answer))}'" for answer in quiz.other_answers("terve")])
        expected_text = f"{Feedback.CORRECT}[answer]Other correct answers are {other_answers}.[/answer]\n"
        feedback = Feedback(quiz, NL_FI)
        self.assertIn(expected_text, feedback.text(Evaluation.CORRECT, GUESS, Retention()))

    def test_show_feedback_on_incorrect_guess(self):
        """Test that the correct feedback is given when the user guesses incorrectly."""
        concept = self.create_concept("hi", labels=[HOI, TERVE])
        (quiz,) = create_quizzes(FI_NL, (DICTATE,), concept)
        expected_text = (
            f"{Feedback.INCORRECT}The correct answer is '{linkified('terve')}'.\n"
            f"[meaning]Meaning '{linkified('hoi')}'.[/meaning]\n"
        )
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(expected_text, feedback.text(Evaluation.INCORRECT, "incorrect", Retention()))

    def test_show_alternative_answers_on_incorrect_guess(self):
        """Test that alternative answers are also given when the user guesses incorrectly."""
        concept = self.create_concept("hi", labels=[HOI, TERVE, HEI])
        (quiz,) = create_quizzes(NL_FI, (READ,), concept)
        expected_text = (
            f"{Feedback.INCORRECT}The correct answers are '{linkified('terve')}' and '{linkified('hei')}'.\n"
        )
        feedback = Feedback(quiz, NL_FI)
        self.assertIn(expected_text, feedback.text(Evaluation.INCORRECT, "incorrect", Retention()))

    def test_do_not_show_generated_alternative_answers_on_incorrect_guess(self):
        """Test that generated alternative answers are not shown when the user guesses incorrectly."""
        concept = self.create_concept(
            "house", labels=[{"label": "het huis", "language": NL}, {"label": "talo", "language": FI}]
        )
        (quiz,) = create_quizzes(FI_NL, (READ,), concept)
        expected_text = f"{Feedback.INCORRECT}The correct answer is '{linkified('het huis')}'.\n"
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(expected_text, feedback.text(Evaluation.INCORRECT, "incorrect", Retention()))

    def test_do_not_show_generated_alternative_answers_on_question_mark(self):
        """Test that generated alternative answers are not shown when the user enters a question mark."""
        concept = self.create_concept(
            "house", labels=[{"label": "het huis", "language": NL}, {"label": "talo", "language": FI}]
        )
        (quiz,) = create_quizzes(FI_NL, (READ,), concept)
        expected_text = f"The correct answer is '{linkified('het huis')}'.\n"
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(expected_text, feedback.text(Evaluation.SKIPPED, "?", Retention()))

    def test_show_feedback_on_question_mark(self):
        """Test that the correct feedback is given when the user doesn't know the answer."""
        concept = self.create_concept("hi", labels=[HOI, TERVE])
        (quiz,) = create_quizzes(FI_NL, (DICTATE,), concept)
        expected_text = (
            f"The correct answer is '{linkified('terve')}'.\n[meaning]Meaning '{linkified('hoi')}'.[/meaning]\n"
        )
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(expected_text, feedback.text(Evaluation.SKIPPED, "?", Retention()))

    def test_show_feedback_on_question_mark_with_multiple_answers(self):
        """Test that the correct feedback is given when the user doesn't know the answer."""
        concept = self.create_concept("hi", labels=[HOI, TERVE, HEI])
        (quiz,) = create_quizzes(NL_FI, (READ,), concept)
        expected_text = f"The correct answers are '{linkified('terve')}' and '{linkified('hei')}'.\n"
        feedback = Feedback(quiz, NL_FI)
        self.assertIn(expected_text, feedback.text(Evaluation.SKIPPED, "?", Retention()))


class FeedbackNotesTest(ToistoTestCase):
    """Unit tests for the notes given by the feedback function."""

    def test_note(self):
        """Test that the post quiz note is formatted correctly."""
        concept = self.create_concept(
            "hi", labels=[{"label": "hoi", "language": NL, "note": "'hoi' is an informal greeting"}]
        )
        (quiz,) = create_quizzes(NL_FI, (DICTATE,), concept)
        feedback = Feedback(quiz, NL_FI)
        self.assertIn(
            f"[note]Note: '{linkified('hoi')}' is an informal greeting.[/note]",
            feedback.text(Evaluation.CORRECT, "hoi", Retention()),
        )

    def test_multiple_notes(self):
        """Test that multiple post quiz notes are formatted correctly."""
        concept = self.create_concept(
            "hi",
            labels=[
                {"label": "moi", "language": FI, "note": ["'moi' is an informal greeting", "'moi moi' means goodbye"]}
            ],
        )
        (quiz,) = create_quizzes(FI_NL, (DICTATE,), concept)
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(
            f"[note]Notes:\n- '{linkified('moi')}' is an informal greeting.\n"
            f"- '{linkified('moi moi')}' means goodbye.[/note]\n",
            feedback.text(Evaluation.CORRECT, "moi", Retention()),
        )

    def test_note_on_incorrect_answer(self):
        """Test that the note is given when the answer is incorrect."""
        concept = self.create_concept(
            "hi", labels=[{"label": "moi", "language": FI, "note": "'moi' is an informal greeting"}]
        )
        (quiz,) = create_quizzes(FI_NL, (DICTATE,), concept)
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(
            f"[note]Note: '{linkified('moi')}' is an informal greeting.[/note]",
            feedback.text(Evaluation.INCORRECT, "toi", Retention()),
        )

    def test_note_on_incorrect_answer_that_has_different_meaning(self):
        """Test that the note is given when the answer is incorrect."""
        self.create_concept("hello", labels=[TERVE, {"label": "hallo", "language": NL}])
        hi = self.create_concept("hi", labels=[{"label": "moi", "language": FI}, HOI])
        (quiz,) = create_quizzes(FI_NL, (INTERPRET,), hi)
        feedback = Feedback(quiz, FI_NL)
        feedback.incorrect_guesses = ["hallo"]
        self.assertIn(
            f"[note]Note: Your incorrect answer '{linkified('hallo')}' is '{linkified('terve')}' in Finnish.[/note]",
            feedback.text(Evaluation.CORRECT, "hoi", Retention()),
        )

    def test_note_on_incorrect_answer_that_has_homograph_meanings(self):
        """Test that the note is given when the answer has two meanings that are homographs."""
        less = self.create_concept(
            "less", labels=[{"label": "vähemmän", "language": FI}, {"label": "minder", "language": NL}]
        )
        self.create_concept("elder", labels=[{"label": "vanhempi", "language": FI}, {"label": "ouder", "language": NL}])
        self.create_concept(
            "older",
            labels=[
                {"label": {"comparative degree": "vanhempi"}, "language": FI},
                {"label": {"comparative degree": "ouder"}, "language": NL},
            ],
        )
        (quiz,) = create_quizzes(FI_NL, (INTERPRET,), less)
        feedback = Feedback(quiz, FI_NL)
        feedback.incorrect_guesses = ["ouder"]
        self.assertIn(
            f"[note]Note: Your incorrect answer '{linkified('ouder')}' is '{linkified('vanhempi')}' in Finnish.[/note]",
            feedback.text(Evaluation.CORRECT, "minder", Retention()),
        )

    def test_note_on_incorrect_answer_that_has_different_meaning_that_is_repeated(self):
        """Test that the note is not repeated if the same incorrect answer is given twice."""
        self.create_concept("hello", labels=[TERVE, {"label": "hallo", "language": NL}])
        hi = self.create_concept("hi", labels=[{"label": "moi", "language": FI}, HOI])
        (quiz,) = create_quizzes(FI_NL, (INTERPRET,), hi)
        feedback = Feedback(quiz, FI_NL)
        feedback.incorrect_guesses = ["hallo"]
        self.assertIn(
            f"[note]Note: Your incorrect answer '{linkified('hallo')}' is '{linkified('terve')}' in Finnish.[/note]",
            feedback.text(Evaluation.INCORRECT, "hallo", Retention()),
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
        (quiz,) = create_quizzes(FI_NL, (INTERPRET,), home)
        feedback = Feedback(quiz, FI_NL)
        feedback.incorrect_guesses = ["huis"]
        self.assertIn(
            f"[note]Note: Your incorrect answer '{linkified('huis')}' is '{linkified('talo')}' in Finnish.[/note]",
            feedback.text(Evaluation.CORRECT, "thuis", Retention()),
        )

    def test_note_on_incorrect_answer_that_has_different_meaning_and_has_different_grammatical_forms(self):
        """Test that the note is given when the answer is incorrect."""
        self.create_concept(
            "house",
            labels=[
                {"label": {"singular": "talo", "plural": "talot"}, "language": FI},
                {"label": {"singular": "huis", "plural": "huizen"}, "language": NL},
            ],
        )
        home = self.create_concept(
            "home",
            labels=[{"label": "koti", "language": FI}, {"label": "thuis", "language": NL}],
        )
        (quiz,) = create_quizzes(FI_NL, (INTERPRET,), home)
        feedback = Feedback(quiz, FI_NL)
        feedback.incorrect_guesses = ["huizen"]
        self.assertIn(
            f"[note]Note: Your incorrect answer '{linkified('huizen')}' is '{linkified('talot')}' in Finnish.[/note]",
            feedback.text(Evaluation.CORRECT, "thuis", Retention()),
        )

    def test_note_on_skip_to_answer(self):
        """Test that the note is given when the user skips to the answer."""
        concept = self.create_concept(
            "hi", labels=[{"label": "moi", "language": FI, "note": "'moi' is an informal greeting"}]
        )
        (quiz,) = create_quizzes(FI_NL, (DICTATE,), concept)
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(
            f"[note]Note: '{linkified('moi')}' is an informal greeting.[/note]",
            feedback.text(Evaluation.SKIPPED, "?", Retention()),
        )


class FeedbackRetentionTest(ToistoTestCase):
    """Unit tests for the retention returned by the feedback function."""

    def create_feedback(self) -> Feedback:
        """Create a feedback fixture."""
        concept = self.create_concept("hi", labels=[HOI, TERVE])
        (quiz,) = create_quizzes(NL_FI, (READ,), concept)
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
            self.assertIn(
                f"[meaning]Meaning '{linkified(str(quiz.question))}'.[/meaning]\n",
                feedback.text(Evaluation.CORRECT, "ingenieur", Retention()),
            )


class FeedbackExampleTest(ToistoTestCase):
    """Unit tests for the examples given by the feedback function."""

    def test_example_with_spelling_alternatives(self):
        """Test that the post quiz example is formatted correctly when the example has spelling alternatives."""
        hi = self.create_concept("hi", {"example": ConceptId("hi alice")}, labels=[HOI, TERVE])
        self.create_concept(
            "hi alice",
            labels=[{"label": ["Moi Alice!", "Hei Alice!"], "language": FI}, {"label": "Hoi Alice!", "language": NL}],
        )
        (quiz,) = create_quizzes(FI_NL, (READ,), hi)
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(
            Feedback.CORRECT
            + (f"[example]Example: '{linkified('Moi Alice!')}' meaning '{linkified('Hoi Alice!')}'[/example]\n"),
            feedback.text(Evaluation.CORRECT, "hoi", Retention()),
        )

    def test_example_with_write_quiz(self):
        """Test that the post quiz example is in the right language when the quiz type is write."""
        hi = self.create_concept("hi", {"example": ConceptId("hi alice")}, labels=[HOI, TERVE])
        self.create_concept(
            "hi alice", labels=[{"label": "Terve Alice!", "language": FI}, {"label": "Hoi Alice!", "language": NL}]
        )
        (quiz,) = create_quizzes(FI_NL, (WRITE,), hi)
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(
            Feedback.CORRECT
            + (f"[example]Example: '{linkified('Terve Alice!')}' meaning '{linkified('Hoi Alice!')}'[/example]\n"),
            feedback.text(Evaluation.CORRECT, GUESS, Retention()),
        )

    def test_example_with_multiple_meanings(self):
        """Test that the post quiz example is not repeated if an example has multiple meanings."""
        hi = self.create_concept("hi", {"example": ConceptId("hi alice")}, labels=[HOI, TERVE])
        self.create_concept(
            "hi alice",
            labels=[
                {"label": "Terve Alice!", "language": FI},
                {"label": "Hoi Alice!", "language": NL},
                {"label": "Hallo Alice!", "language": NL},
            ],
        )
        (quiz,) = create_quizzes(FI_NL, (WRITE,), hi)
        feedback = Feedback(quiz, FI_NL)
        self.assertIn(
            Feedback.CORRECT
            + f"[example]Example: '{linkified('Terve Alice!')}' meaning '{linkified('Hoi Alice!')}' and "
            f"'{linkified('Hallo Alice!')}'[/example]\n",
            feedback.text(Evaluation.CORRECT, GUESS, Retention()),
        )

    def test_example_with_colloquial_labels(self):
        """Test examples with colloquial labels."""
        hi = self.create_concept("hi", {"example": ConceptId("hi alice")}, labels=[HOI, TERVE])
        self.create_concept(
            "hi alice",
            labels=[
                {"label": "Terve Alice!", "language": FI},
                {"label": "Moi Alice!", "language": FI, "colloquial": True},
                {"label": "Hallo Alice!", "language": NL},
                {"label": "Hoi Alice!", "language": NL, "colloquial": True},
            ],
        )
        (quiz,) = create_quizzes(FI_NL, (WRITE,), hi)
        feedback = Feedback(quiz, FI_NL)
        expected_feedback = f"""{Feedback.CORRECT}[example]Examples:
- '{linkified("Moi Alice!")}' (colloquial) meaning '{linkified("Hallo Alice!")}' and '{linkified("Hoi Alice!")}' \
(colloquial).
- '{linkified("Terve Alice!")}' meaning '{linkified("Hallo Alice!")}' and '{linkified("Hoi Alice!")}' (colloquial).\
[/example]
"""
        self.assertIn(expected_feedback, feedback.text(Evaluation.CORRECT, GUESS, Retention()))

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
        (quiz,) = create_quizzes(FI_NL, (READ,), near)
        feedback = Feedback(quiz, FI_NL)
        expected_feedback = f"""{Feedback.CORRECT}\
[answer]Another correct answer is '{linkified("dichtbij")}'.[/answer]
[example]Example: '{linkified("Se on lähellä.")}' meaning '{linkified("Het is dichtbij.")}' and \
'{linkified("Het is in de buurt.")}'[/example]
"""
        self.assertIn(expected_feedback, feedback.text(Evaluation.CORRECT, "in de buurt", Retention()))

    def test_limit_the_number_of_examples(self):
        """Test that the number of examples shown is limited."""
        names = ["Alice", "Bob", "Carol", "David"]
        hi = self.create_concept("hi", {"example": [ConceptId(f"hi {name}") for name in names]}, labels=[HOI, TERVE])
        for name in names:
            self.create_concept(
                f"hi {name}",
                labels=[{"label": f"Terve {name}!", "language": FI}, {"label": f"Hoi {name}!", "language": NL}],
            )
        (quiz,) = create_quizzes(FI_NL, (WRITE,), hi)
        text = Feedback(quiz, FI_NL).text(Evaluation.CORRECT, GUESS, Retention())
        examples = [f"- '{linkified(f'Terve {name}!')}' meaning '{linkified(f'Hoi {name}!')}'" for name in names]
        self.assertTrue(
            (examples[0] not in text and examples[1] in text and examples[2] in text and examples[3] in text)
            or (examples[0] in text and examples[1] not in text and examples[2] in text and examples[3] in text)
            or (examples[0] in text and examples[1] in text and examples[2] not in text and examples[3] in text)
            or (examples[0] in text and examples[1] in text and examples[2] in text and examples[3] not in text)
        )


class WelcomeTest(ToistoTestCase):
    """Test the welcome message."""

    def setUp(self) -> None:
        """Extend to add mock."""
        super().setUp()
        patcher = patch("rich.console.Console.print")
        self.patched_print = patcher.start()
        self.addCleanup(patcher.stop)

    @staticmethod
    def create_config(target: str = "fi", source: str = "nl") -> ConfigParser:
        """Create a config fixture."""
        config = default_config()
        config.add_section("languages")
        if target:
            config["languages"]["target"] = target
        if source:
            config["languages"]["source"] = source
        return config

    def assert_output(self, *expected_renderables: str | Panel) -> None:
        """Check the output."""
        renderables = []
        for call in self.patched_print.call_args_list:
            renderables.extend(call[0])
        for expected_renderable, renderable in zip(expected_renderables, renderables, strict=True):
            inner_renderable = renderable.renderable if isinstance(renderable, Panel) else renderable
            self.assertEqual(expected_renderable, inner_renderable)

    def test_default_message(self) -> None:
        """Test the default message."""
        show_welcome("", self.create_config())
        self.assert_output(WELCOME)

    def test_show_new_version(self) -> None:
        """Test that a new version is announced."""
        show_welcome("v9999", self.create_config())
        self.assert_output(WELCOME, NEWS.format("v9999"), "")

    def test_do_not_show_old_version(self) -> None:
        """Test that a new version is not announced if the current version is newer."""
        show_welcome("v0", self.create_config())
        self.assert_output(WELCOME)

    def test_do_not_show_current_version(self) -> None:
        """Test that a new version is not announced if it's the current version."""
        show_welcome(f"v{VERSION}", self.create_config())
        self.assert_output(WELCOME)

    def test_show_language_tip_when_no_languages_are_configured(self) -> None:
        """Test that a tip is shown when the user has configured one language."""
        show_welcome("", default_config())
        self.assert_output(WELCOME, CONFIG_LANGUAGE_TIP, "")

    def test_show_language_tip_when_only_source_language_is_configured(self) -> None:
        """Test that a tip is shown when the user hasn't configured languages."""
        show_welcome("", self.create_config(target=""))
        self.assert_output(WELCOME, CONFIG_LANGUAGE_TIP, "")

    def test_show_language_tip_when_only_target_language_is_configured(self) -> None:
        """Test that a tip is shown when the user hasn't configured languages."""
        show_welcome("", self.create_config(source=""))
        self.assert_output(WELCOME, CONFIG_LANGUAGE_TIP, "")

    def test_language_tip_is_not_shown_when_there_is_a_new_version(self) -> None:
        """Test that the language config tip is not shown when a new version is announced."""
        show_welcome("v9999", default_config())
        self.assert_output(WELCOME, NEWS.format("v9999"), "")
