"""Command-line interface."""

import argparse

from importlib.metadata import metadata, version


parser = argparse.ArgumentParser(description=metadata("Toisto")["summary"])
parser.add_argument("-V", "--version", action="version", version=version("Toisto"))
