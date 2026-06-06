"""Practice command."""

from argparse import Namespace
from configparser import ConfigParser
from dataclasses import dataclass
from typing import Final

import dramatic
from rich.control import Control
from rich.segment import ControlType

from toisto.model.language import LanguagePair
from toisto.model.quiz.evaluation import Evaluation
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quiz
from toisto.model.quiz.quiz_type import ListenOnlyQuizType
from toisto.persistence.progress import save_progress
from toisto.ui.dictionary import linkified
from toisto.ui.speech import Speech
from toisto.ui.text import CONTINUE, DONE, Feedback, ProgressUpdate, console, instruction

# Mode for the ANSI "Erase in Line" (CSI n K) control code; 2 means erase the entire line (0 = cursor to end of
# line, 1 = start of line to cursor, 2 = whole line).
ERASE_ENTIRE_LINE: Final = 2


@dataclass(frozen=True)
class QuizMaster:
    """Do quizzes."""

    language_pair: LanguagePair
    progress: Progress
    speech: Speech
    show_quiz_retention: bool

    def do_quiz(self, quiz: Quiz) -> None:
        """Do one quiz and update the progress."""
        feedback = Feedback(quiz, self.language_pair)
        console.print(instruction(quiz))
        if not quiz.has_quiz_type(ListenOnlyQuizType):
            console.print(linkified(str(quiz.question)))
        for attempt in range(1, 3):
            guess = self.do_quiz_attempt(quiz, attempt)
            evaluation = quiz.evaluate(guess, self.language_pair.source, attempt)
            retention = self.progress.mark_evaluation(quiz, evaluation)
            console.print(feedback.text(evaluation, guess, retention if self.show_quiz_retention else None))
            if evaluation in (Evaluation.SKIPPED, Evaluation.INCORRECT):
                self.say_answer(quiz)
                self.wait_for_keypress()
            if evaluation in (Evaluation.CORRECT, Evaluation.SKIPPED):
                break

    def say_answer(self, quiz: Quiz) -> None:
        """Say the correct answer, but only if it is in the target language; no need to speak the source language."""
        if quiz.answer.language == self.language_pair.target:
            self.speech.say(quiz.answer.language, quiz.answer.pronounceable, slow=True)

    def wait_for_keypress(self) -> None:
        """Wait for the user to press Enter before showing the next quiz, so they can read the correct answer."""
        console.print(CONTINUE, end="")
        input()
        # Move the cursor to the start of the previous line and erase it, to remove the "Press Enter" prompt.
        console.control(Control.move_to_column(0, -1), Control((ControlType.ERASE_IN_LINE, ERASE_ENTIRE_LINE)))

    def do_quiz_attempt(self, quiz: Quiz, attempt: int) -> str:
        """Present the question and get the answer from the user."""
        repeat_speech = False
        while True:
            self.speech.say(quiz.question.language, quiz.question.pronounceable, slow=repeat_speech or attempt > 1)
            if answer := input("> ").strip():
                break
            repeat_speech = True
            console.control(Control.move_to_column(0, -1))  # Move the cursor to the start of the previous line
        return answer


def practice(language_pair: LanguagePair, progress: Progress, config: ConfigParser, args: Namespace) -> None:
    """Practice a language."""
    progress_update = ProgressUpdate(progress, args.progress_update)
    speech = Speech(config)
    quiz_master = QuizMaster(language_pair, progress, speech, args.show_quiz_retention == "yes")
    try:
        while quiz := progress.next_quiz():
            quiz_master.do_quiz(quiz)
            save_progress(progress, config)
            with dramatic.output.at_speed(120):
                # Turn off highlighting to work around https://github.com/treyhunner/dramatic/issues/8:
                console.print(progress_update(), end="", highlight=False)
        console.print(DONE)
    except (KeyboardInterrupt, EOFError):
        console.print()  # Make sure the shell prompt is displayed on a new line
