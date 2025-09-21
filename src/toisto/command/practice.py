"""Practice command."""

from argparse import Namespace
from collections.abc import Callable
from configparser import ConfigParser
from dataclasses import dataclass

import dramatic

from toisto.model.language import LanguagePair
from toisto.model.quiz.evaluation import Evaluation
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quiz
from toisto.model.quiz.quiz_type import ListenOnlyQuizType
from toisto.persistence.progress import save_progress
from toisto.ui.dictionary import linkified
from toisto.ui.speech import Speech
from toisto.ui.text import DONE, Feedback, ProgressUpdate, instruction


@dataclass(frozen=True)
class QuizMaster:
    """Do quizzes."""

    write_output: Callable[..., None]
    language_pair: LanguagePair
    progress: Progress
    speech: Speech
    show_quiz_retention: bool

    def do_quiz(self, quiz: Quiz) -> None:
        """Do one quiz and update the progress."""
        feedback = Feedback(quiz, self.language_pair)
        self.write_output(instruction(quiz))
        if not quiz.has_quiz_type(ListenOnlyQuizType):
            self.write_output(linkified(str(quiz.question)))
        for attempt in range(1, 3):
            guess = self.do_quiz_attempt(quiz, attempt)
            evaluation = quiz.evaluate(guess, self.language_pair.source, attempt)
            retention = self.progress.mark_evaluation(quiz, evaluation)
            self.write_output(feedback.text(evaluation, guess, retention if self.show_quiz_retention else None))
            if evaluation in (Evaluation.CORRECT, Evaluation.SKIPPED):
                break

    def do_quiz_attempt(self, quiz: Quiz, attempt: int) -> str:
        """Present the question and get the answer from the user."""
        repeat_speech = False
        while True:
            self.speech.say(quiz.question.language, quiz.question.pronounceable, slow=repeat_speech or attempt > 1)
            if answer := input("> ").strip():
                break
            repeat_speech = True
            print("\033[F", end="")  # noqa: T201  # Move cursor one line up
        return answer


def practice(
    write_output: Callable[..., None],
    language_pair: LanguagePair,
    progress: Progress,
    config: ConfigParser,
    args: Namespace,
) -> None:
    """Practice a language."""
    progress_update = ProgressUpdate(progress, args.progress_update)
    speech = Speech(config)
    quiz_master = QuizMaster(write_output, language_pair, progress, speech, args.show_quiz_retention == "yes")
    try:
        while quiz := progress.next_quiz():
            quiz_master.do_quiz(quiz)
            save_progress(progress, config)
            with dramatic.output.at_speed(120):
                # Turn off highlighting to work around https://github.com/treyhunner/dramatic/issues/8:
                write_output(progress_update(), end="", highlight=False)
        write_output(DONE)
    except (KeyboardInterrupt, EOFError):
        write_output()  # Make sure the shell prompt is displayed on a new line
