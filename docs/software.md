# Software documentation

## Topics

Builtin topics are located in `src/topics` in the form of JSON files. Users can also create their own topic files as long as it complies with the description below and pass them to Toisto using the `-t/--topic-file` command-line option.

Each topic is a list of *concepts* with *labels* in different languages. A concept can be anything that can be expressed in language. The labels are words, phrases, or sentences that express the concept in a specific language.

The contents of a JSON topic file look as follows:

```json
[
    {
        "en": "Today",
        "fi": "Tänään",
        "nl": "Vandaag"
    },
    {
        "en": "Yesterday",
        "fi": "Eilen",
        "nl": "Gisteren"
    },
    {
        "en": "Tomorrow",
        "fi": "Huomenna",
        "nl": "Morgen"
    }
]
```

Concepts are represented in the topic files as JSON mappings with language identifiers as keys and labels as values. Currently supported language identifiers are `en` for English, `fi` for Finnish, and `nl` for Dutch.

When using more than two languages is not essential to explain how things work, examples below may contain just two languages.

### Spelling variants

When there are multiple ways to spell a label, use the pipe symbol to separate the alternatives. Toisto will only use the first of the alternatives to quiz the user, but will accept the other alternatives as answer.

```json
[
    {
        "en": "Tomorrow it is Tuesday|Tomorrow it's Tuesday",
        "fi": "Huomenna on tiistai"
    }
]
```

### Concepts with multiple labels

Labels consist of either one string or a list of strings. A list of strings is used when there are multiple equivalent ways to express the concept in a language, as with "Mikä päivä tänään on?" and "Mikä päivä on tänään?" below. Toiso will quiz the user with each synonym, so in the example below users practicing Finnish will be asked to translate both Finnish sentences.

```json
[
    {
        "en": "What day is it today?",
        "fi": [
            "Mikä päivä tänään on?",
            "Mikä päivä on tänään?"
        ]
    }
]
```

### Multiple concepts with the same label

Sometimes a concept in one language can be two different concepts in another language. For example, both in English and Dutch there are separate greetings for the afternoon and the whole day: "Good afternoon" and "Good day" in English and "Goedemiddag" and "Goedendag" in Dutch. In Finnish "Hyvää päivää", or just "Päivää", is used for both. As an aside, "Hyvää iltapäivää", although grammatically correct, is not used.

If we would include all these labels in one concept, Toisto would consider "Goedemiddag" a correct translation of "Good day", which is undesirable. The solution is to distribute the labels over four different concepts:

- One concept with the labels "Goedemiddag" and "Good afternoon" and one concept with the labels "Goedendag" and "Good day", both without Finnish labels. This ensures that "Goedemiddag" is not considered to be a correct translation of "Good day".
- One concept with the Finnish labels "Hyvää päivää" and "Päivää" and with both Dutch labels, "Goedendag" and "Goedemiddag" and one concept with the Finnish labels "Hyvää päivää" and "Päivää" and with both English labels, "Good day" and "Good afternoon". This ensures that "Goedendag", "Goedemiddag", "Good day", and "Good afternoon" are all correct translations for "Hyvää päivää" and "Päivää". Unfortunately, we cannot put the English and Dutch labels in one concept with the Finnish labels because otherwise Toisto would still consider "Goedemiddag" to be a correct translation of "Good day".

In the topic file this looks as follows:

```json
[
    {
        "en": "Good day",
        "nl": "Goedendag"
    },
    {
        "en": "Good afternoon",
        "nl": "Goedemiddag"
    },
    {
        "fi": [
            "Hyvää päivää",
            "Päivää"
        ],
        "en": [
            "Good afternoon",
            "Good day"
        ]
    },
    {
        "fi": [
            "Hyvää päivää",
            "Päivää"
        ],
        "nl": [
            "Goedendag",
            "Goedemiddag"
        ]
    }
]
```

### Grammatical number

When concepts can have both singular and plural forms, such as with most nouns, these are represented in the JSON as mappings with `singular` and `plural` as keys and concepts as values.

The format of the JSON files is as follows:

```json
[
    {
        "singular": {
            "en": "Day",
            "fi": "Päivä",
            "nl": "De dag"
        },
        "plural": {
            "en": "Days",
            "fi": "Päivät",
            "nl": "De dagen"
        }
    }
]
```

### Grammatical person

When concepts, usually verbs and pronouns, have different persons, these are represented in the JSON as mappings with `first_person`, `second_person`, and `third_person`.

The format of the JSON files is as follows:

```json
[
    {
        "singular": {
            "first_person": {
                "en": "I have|I've",
                "fi": "Minulla on"
            },
            "second_person": {
                "en": "You have|You've;singular",
                "fi": "Sinulla on"
            },
            "third_person": {
                "en": ["She has", "He has"],
                "fi": "Hänellä on"
            }
        },
        "plural": {
            "first_person": {
                "en": "We have|We've",
                "fi": "Meillä on"
            },
            "second_person": {
                "en": "You have|You've;plural",
                "fi": "Teillä on"
            },
            "third_person": {
                "en": "They have|They've",
                "fi": "Heillä on"
            }
        }
    }
]
```

Note that because the second person singular and plural are the same in English, Toisto needs to tell the user whether it is asking for a translation of the singular version or the plural version of "You are". The hint is the part after the ";".

Using grammatical gender to further specify the third person singular is not possible at the moment. Fixing [issue #11](https://github.com/fniessink/toisto/issues/11)) should correct that.

### Grammatical gender

When concepts have multiple genders, these can be specified as follows:

```json
[
    {
        "female": {
            "en": "Mother",
            "nl": "De moeder"
        },
        "male": {
            "en": "Father",
            "nl": "De vader"
        }
    }
]
```

It's also possible to have a neutral gender:

```json
[
    {
        "female": {
            "en": "Mother",
            "nl": "De moeder"
        },
        "male": {
            "en": "Father",
            "nl": "De vader"
        },
        "neuter": {
            "en": "Parent",
            "nl": "De ouder
        }
    }
]
```

### Degrees of comparison

Degrees of comparison are specified as follows:

```json
[
    {
        "positive_degree": {
            "en": "Small",
            "nl": "Klein"
        },
        "comparitive_degree": {
            "en": "Smaller",
            "nl": "Kleiner"
        },
        "superlative_degree": {
            "en": "Smallest",
            "nl": "Kleinst"
        }
    }
]
```

When there are synonyms, they need to be in the same order in every degree. This makes sure Toisto does not consider "Suurin" a superlative of "Iso".

```json
[
    {
        "positive_degree": {
            "en": "Big",
            "fi": ["Iso", "Suuri"],
            "nl": "Groot"
        },
        "comparitive_degree": {
            "en": "Bigger",
            "fi": ["Isompi", "Suurempi"],
            "nl": "Groter"
        },
        "superlative_degree": {
            "en": "Biggest",
            "fi": ["Isoin", "Suurin"],
            "nl": "Grootst"
        }
    }
]
```

## Quizzes

Toisto uses the concepts to generate quizzes. Currently, the following types of quizzes are generated:

1. Quizzes to translate a concept from one language to another and vice versa. Toisto quizzes the user in both directions. If there are multiple labels, Toisto uses all labels as question and as answer. So both "Mikä päivä tänään on?" and "Mikä päivä on tänään?" are asked as question and both are accepted as correct answer for the quiz "What day is it today?".
2. Quizzes to listen to a concept in the practice language and then type in what was said.
3. Quizzes to singularize a plural concept or pluralize a singular concept.
4. Quizzes to change the person of a concept.
5. Quizzes to change the gender of a concept.
6. Quizzes to provide the positive, comparitive, or superlative degree of comparison, given an adjective in another degree.

Except for the translation type quizzes, quizzes only use the user's practice language.

## Spaced repetition

Toisto uses a very simple implementation of a spaced repetition algorithm. Toisto does not make assumptions about how many concepts the user wants to practice per session or per day. It only keeps track of how many times in a row a specific quiz is answered correctly. When a quiz is answered correctly twice or more in a row, the quiz is silenced for a while. The longer the streak, the longer the quiz is silenced. The exact amount is determined by a [S-curve with a maximum value of 90 days](https://www.desmos.com/calculator/itvdhmh6ex). Whenever the user makes a mistake the streak is reset to zero.
