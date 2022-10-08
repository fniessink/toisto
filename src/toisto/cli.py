"""Command-line interface."""

import argparse

from .metadata import SUMMARY, VERSION


parser = argparse.ArgumentParser(description=SUMMARY)
parser.add_argument("-V", "--version", action="version", version=VERSION)
