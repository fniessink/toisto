# Software documentation

## Concepts and labels

Built-in concepts are located in `src/concepts` in the form of JSON files. See the documentation on the [concept file format](./concept_files.md) for more information.

## Quizzes

Toisto uses the concepts to generate quizzes. Currently, the following types of quizzes are generated:

Translation quizzes:

1. Translate a concept from the target language to the source language.
2. Listen to a concept in the target language and then type in what was said.
3. Translate a concept from the source language to the target language.
4. Listen to a concept in the target language and then translate what was said in the source language.

Grammatical quizzes:

5. Singularize a plural concept or pluralize a singular concept.
6. Diminutize a concept.
7. Change the person of a concept.
8. Change the gender of a concept.
9. Provide the positive, comparative, or superlative degree of comparison, given an adjective in another degree.
10. Change the tense of a concept between infinitive, present tense, and past tense.
11. Change the aspect of a concept from perfective to imperfective and vice versa.
12. Change the grammatical mood of a concept between declarative, interrogative, and imperative mood.
13. Change the polarity from affirmative to negative and vice versa.
14. Change cardinal numbers into ordinal numbers and vice versa.
15. Change the grammatical case of a noun (nominative ↔ partitive).
16. Fill in the missing inflected word in a sentence (cloze test).

Semantic quizzes:

17. Give the antonym.
18. Answer a question.
19. Abbreviate a concept or give the full-form of the abbreviation.
20. Put the words of a shuffled sentence in the right order.

Except when asking the user to translate from the source language to the target language, quizzes only use the user's target language.

## Extending grammatical categories

To add a new grammatical case (e.g., `"genitive"`) or another value of an existing grammatical category, edit:

1. **`src/toisto/model/language/grammatical_category.py`** — add the value to the relevant `Literal` type (e.g., `GrammaticalCase`). If the value is meaning-changing across languages — i.e., it should *not* be accepted as a translation of the unmarked form in another language — also add it to `SEMANTIC_NON_DEFAULT_CATEGORIES`. The default value of a category (e.g., `"nominative"` for case) belongs in `DEFAULT_CATEGORIES` instead.

2. **`src/toisto/model/quiz/quiz_type.py`** — define a `GrammaticalQuizType` instance for the value (e.g., `GENITIVE = GrammaticalQuizType("genitive")`) and append it to `GRAMMATICAL_QUIZ_TYPES`.

3. **`docs/concept_files.md`** — list the new value in the relevant section so concept authors know they can use it.

Concept JSON files can then use the value as a nested key in label objects; the label factory and quiz generator handle it without further changes.

## Spaced repetition

Toisto uses a very simple implementation of a spaced repetition algorithm. Toisto does not make assumptions about how many concepts the user wants to practice per session or per day. It only keeps track of the retention of quizzes, i.e. how long the user has been correctly answering a quiz. Retention is defined as the time between the most recent correct answer and the oldest correct answer, where there have been no incorrect answers in between.

For example, if a user answers a quiz correctly on March 1, incorrectly on March 3, correctly on March 6, correctly on March 8, and correctly on March 15, that quiz has a retention of nine days (March 6 to March 15).

Each time a quiz is answered correctly, the quiz is silenced for a while. The longer the quiz's current retention, the longer the quiz is silenced. Whenever the user makes a mistake the retention is reset to zero.

If a user knows the correct answer the first time a quiz is presented, the quiz is silenced for a longer duration (24 hours).

## Progress savefile

When the program is stopped, progress is saved in a file named `.toisto-{device specific id}-progress-{target language}.json` in the user's home folder, for example `.toisto-c5323926-33e2-1eef-a453-2922a2aed6c5-progress-fi.json`. So each target language gets its own progress file.

Each entry in the file is the progress of one specific quiz. The key denotes the quiz, the value contains information about the user's retention of the quiz. This looks as follows:

```json
{
    "nl:fi:lezen:lukea:translate": {
        "count": 2
    },
    "nl:fi:het oog:silmä:translate": {
        "start": "2023-02-25T17:34:37",
        "end": "2023-02-25T17:35:37",
        "skip_until": "2023-02-26T17:40:37",
        "count": 3
    }
}
```

The key format was changed in Toisto v0.28 to not include the concept identifier. This allows for changing the concept identifier without invalidating the user's progress on quizzes for that concept. Whenever Toisto reads a progress file with keys in the old format, it converts the keys the new format, where possible (it can only do so for concepts the user wants to practice). The old format looks as follows:

```json
{
    "to read:nl:fi:lezen:translate": {
        "count": 2
    },
    "eye:nl:fi:het oog:translate": {
        "start": "2023-02-25T17:34:37",
        "end": "2023-02-25T17:35:37",
        "skip_until": "2023-02-26T17:40:37",
        "count": 3
    }
}
```

The first entry is the quiz to translate "lezen" from Dutch to Finnish. This quiz has been presented to the user twice (`count` is 2), but they haven't answered it correctly since the last time it was presented.

The second entry is the quiz to translate "het oog" from Dutch to Finnish. This quiz has been presented to the user three times (`count` is 3) in the period between `start` and `end` and they have answered it correctly each time. Toisto will not present to quiz again until after `skip_until`.

The keys in the savefile contain the question label of quizzes. That means that when the label of a concept changes, for example to fix spelling, progress on quizzes that use the label will be lost.
