"""Easter egg."""

import time
import webbrowser
from argparse import ArgumentParser

from toisto.ui.text import console


def show_easter_egg(argument_parser: ArgumentParser) -> None:
    """Show the easter egg."""
    console.print("🎉🐇🐣 Happy Easter! 🎉🐇🐣\n")
    time.sleep(1.0)
    console.print("Here are some ideas to do")
    time.sleep(1.0)
    console.print("over the Easter weekend")
    time.sleep(1.0)
    console.print("instead of practicing a language...")
    time.sleep(2.0)
    webbrowser.open("https://nl.pinterest.com/melliejacobs/pasen-paasei/")
    argument_parser.exit()
