"""Common European Framework of Reference for Languages (CEFR)."""

from typing import Literal

# Source: https://www.coe.int/en/web/common-european-framework-reference-languages/level-descriptions
CommonReferenceLevel = Literal["A1", "A2", "B1", "B2", "C1", "C2"]

# Toisto uses different sources to assess the common reference level for concepts:
CommonReferenceLevelSource = Literal["EP", "KK", "OD"]

SOURCES: dict[CommonReferenceLevelSource, dict[Literal["name", "url", "language"], str]] = dict(
    EP=dict(
        name="English Vocabulary Profile Online - British English",
        url="https://www.englishprofile.org/wordlists/evp",
        language="en",
    ),
    KK=dict(name="Yle Kielikoulu Learning Profile", url="https://kielikoulu.yle.fi/#/profile", language="fi"),
    OD=dict(
        name="Oxford Advanced Learner's Dictionary online",
        url="https://www.oxfordlearnersdictionaries.com",
        language="en",
    ),
)
