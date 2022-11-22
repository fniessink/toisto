# Software documentation

## Topics

Builtin topics are located in `src/topics` in the form of JSON files. Users can also create their own topic files as long as it complies with the description below and pass them to Toisto using the `-t/--topic-file` command-line option.

Each topic is a collection of *concepts*. Each concept has *labels* in different languages. A concept can be anything that can be expressed in language. The labels are words, phrases, or sentences that express the concept in a specific language.

The contents of a JSON topic file looks as follows:

```json
{
    "today": {
        "en": "Today",
        "fi": "Tänään",
        "nl": "Vandaag"
    },
    "yesterday": {
        "en": "Yesterday",
        "fi": "Eilen",
        "nl": "Gisteren"
    },
    "tomorrow": {
        "en": "Tomorrow",
        "fi": "Huomenna",
        "nl": "Morgen"
    }
}
```

Concepts are represented in the topic files as objects. The key is an identifier for the concept. The value is a mapping with language identifiers as keys and labels as values. Currently supported language identifiers are `en` for English, `fi` for Finnish, and `nl` for Dutch.

When using more than two languages is not essential to explain how things work, examples below may contain just two languages.

### Spelling variants

When there are multiple ways to spell a label, use the pipe symbol to separate the alternatives. Toisto will only use the first of the alternatives to quiz the user, but will accept the other alternatives as answer.

```json
{
    "tomorrow it is tuesday": {
        "en": "Tomorrow it is Tuesday|Tomorrow it's Tuesday",
        "fi": "Huomenna on tiistai"
    }
}
```

### Concepts with multiple labels

Labels consist of either one string or a list of strings. A list of strings is used when there are multiple equivalent ways to express the concept in a language, as with "Mikä päivä tänään on?" and "Mikä päivä on tänään?" below. Toiso will quiz the user with each synonym, so in the example below users practicing Finnish will be asked to translate both Finnish sentences.

```json
{
    "what day is it today": {
        "en": "What day is it today?",
        "fi": [
            "Mikä päivä tänään on?",
            "Mikä päivä on tänään?"
        ]
    }
}
```

### Multiple concepts with the same label

Sometimes a concept in one language can be two different concepts in another language. For example, both in English and Dutch there are separate greetings for the afternoon and the whole day: "Good afternoon" and "Good day" in English and "Goedemiddag" and "Goedendag" in Dutch. In Finnish "Hyvää päivää", or just "Päivää", is used for both. As an aside, "Hyvää iltapäivää", although grammatically correct, is not used.

If we would include all these labels in one concept, Toisto would consider "Goedemiddag" a correct translation of "Good day", which is undesirable. The solution is to distribute the labels over four different concepts:

- One concept with the labels "Goedemiddag" and "Good afternoon" and one concept with the labels "Goedendag" and "Good day", both without Finnish labels. This ensures that "Goedemiddag" is not considered to be a correct translation of "Good day".
- One concept with the Finnish labels "Hyvää päivää" and "Päivää" and with both Dutch labels, "Goedendag" and "Goedemiddag" and one concept with the Finnish labels "Hyvää päivää" and "Päivää" and with both English labels, "Good day" and "Good afternoon". This ensures that "Goedendag", "Goedemiddag", "Good day", and "Good afternoon" are all correct translations for "Hyvää päivää" and "Päivää". Unfortunately, we cannot put the English and Dutch labels in one concept with the Finnish labels because otherwise Toisto would still consider "Goedemiddag" to be a correct translation of "Good day".

In the topic file this looks as follows:

```json
{
    "good day": {
        "en": "Good day",
        "nl": "Goedendag"
    },
    "good afternoon": {
        "en": "Good afternoon",
        "nl": "Goedemiddag"
    },
    "good day fi:en": {
        "fi": [
            "Hyvää päivää",
            "Päivää"
        ],
        "en": [
            "Good afternoon",
            "Good day"
        ]
    },
    "good day fi:nl": {
        "fi": [
            "Hyvää päivää",
            "Päivää"
        ],
        "nl": [
            "Goedendag",
            "Goedemiddag"
        ]
    }
}
```

### Grammatical number

When concepts can have both singular and plural forms, such as with most nouns, these are represented in the JSON as mappings with `singular` and `plural` as keys and concepts as values.

The format of the JSON files is as follows:

```json
{
    "day": {
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
}
```

### Grammatical gender

When concepts have multiple genders, these can be specified as follows:

```json
{
    "parent": {
        "female": {
            "en": "Mother",
            "nl": "De moeder"
        },
        "male": {
            "en": "Father",
            "nl": "De vader"
        }
    }
}
```

It is also possible to have a neutral gender:

```json
{
    "parent": {
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
            "nl": "De ouder"
        }
    }
}
```

Note that Toisto uses gender only for verbs at the moment, see the next section. The examples above are not in the builtin topic files.

### Grammatical person

When concepts, usually verbs and pronouns, have different persons, these are represented in the JSON as mappings with `first_person`, `second_person`, and `third_person`.

The format of the JSON files is as follows:

```json
{
    "to have": {
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
                "female": {
                    "en": "She has|She's",
                    "fi": "Hänellä on;female"
                },
                "male": {
                    "en": "He has|He's",
                    "fi": "Hänellä on;male"
                }
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
}
```

Note that because the second person singular and plural are the same in English, Toisto needs to tell the user whether it is asking for a translation of the singular version or the plural version of "You are". The hint is the part after the `;`.

The same goes for the third person Finnish. Because Finnish does not distinguish between male and female gender, Toisto needs to tell the user whether it is asking for the female or the male translation of "Hänellä on".

### Degrees of comparison

Degrees of comparison are specified as follows:

```json
{
    "small": {
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
}
```

When there are synonyms, they need to be in the same order in every degree. This makes sure Toisto does not consider "Suurin" a superlative of "Iso".

```json
{
    "big": {
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
}
```

### Concept relationships

When a concept uses one or more other concepts, this can be specified with the `uses` relation. Toisto will only quiz a *using* concept when all *used* concepts have been quizzed. The `uses` relationship can be specified by adding a `uses` key to the concept with a list of concept identifiers as value:

```json
{
    "day": {
        "singular": {
            "en": "Day",
            "nl": "De dag"
        },
        "plural": {
            "en": "Days",
            "nl": "De dagen"
        }
    },
    "week": {
        "singular": {
            "en": "Week",
            "nl": "De week"
        },
        "plural": {
            "en": "Weeks",
            "nl": "De weken"
        }
    },
    "days of the week": {
        "uses": ["day", "week"],
        "en": "Days of the week",
        "nl": "De dagen van de week"
    }
}
```

If a concept uses exactly one other concept, the `uses` value can be a string instead of a list of concept identifiers.

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

Toisto uses a very simple implementation of a spaced repetition algorithm. Toisto does not make assumptions about how many concepts the user wants to practice per session or per day. It only keeps track of the retention of quizzes, i.e. how long the user has been correctly answering a quiz. Retention is defined as the time between the most recent correct answer and the oldest correct answer, where there have been no incorrect answers in between.

For example, if a user answers a quiz correctly on March 1, incorrectly on March 3, correctly on March 6, correctly on March 8, and correctly on March 15, that quiz has a retention of nine days (March 6 to March 15).

Each time a quiz is answered correctly, the quiz is silenced for a while. The longer the quiz's current retention, the longer the quiz is silenced. Whenever the user makes a mistake the retention is reset to zero.

If a user knows the correct answer the first time a quiz is presented, the quiz is silenced for a longer duration (24 hours).
