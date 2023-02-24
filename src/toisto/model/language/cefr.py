"""Common European Framework of Reference for Languages (CEFR).

See https://www.coe.int/en/web/common-european-framework-reference-languages/level-descriptions

Used sources for the language levels of words are:
- EP: [English Vocabulary Profile Online - British English (en)](https://www.englishprofile.org/wordlists/evp")
- KK: [Yle Kielikoulu Learning Profile (fi)]("https://kielikoulu.yle.fi/#/profile")
- OD: [Oxford Advanced Learner's Dictionary online (en)]("https://www.oxfordlearnersdictionaries.com")
"""

from typing import Literal

# The levels defined by the Common European Framework of Reference for Languages:
CommonReferenceLevel = Literal["A1", "A2", "B1", "B2", "C1", "C2"]

# Toisto uses different sources to assess the common reference level for concepts:
CommonReferenceLevelSource = Literal["EP", "KK", "OD"]
