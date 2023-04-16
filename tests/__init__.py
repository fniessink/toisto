"""Unit tests."""

import logging
import sys
from pathlib import Path

logging.getLogger().setLevel(logging.ERROR)

src_folder = Path(__file__).parent / ".." / "src"
sys.path.insert(0, str(src_folder.resolve()))
