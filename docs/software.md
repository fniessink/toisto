# Software documentation

## Concepts and labels

Built-in concepts are located in `src/concepts` in the form of JSON files.

Users can also create their own files as long as they comply with the description below and pass them to Toisto using the `-f/--file` command-line option.

Each JSON file contains one or more *concepts*. Each concept has *labels* in different languages, identified by *language identifiers*.

A concept can be anything that can be expressed in language. The labels are words, phrases, or sentences that express the concept in a specific language. The language identifiers are two or three letter strings as listed in the [IANA language subtag registry](https://www.iana.org/assignments/language-subtag-registry).

The contents of a JSON file looks as follows:

```json
{
    "concepts": {
        "today": {
            "en": "today",
            "fi": "tänään",
            "nl": "vandaag"
        },
        "yesterday": {
            "en": "yesterday",
            "fi": "eilen",
            "nl": "gisteren",
        },
        "tomorrow": {
            "en": "tomorrow",
            "fi": "huomenna",
            "nl": "morgen"
        }
    }
}
```

Concepts are represented in the JSON files as JSON objects. The key is an identifier for the concept. It should be unique across all JSON files. The value is a mapping with language identifiers as keys and labels as values. Currently, the built-in JSON files contain English with identifier `en`, Finnish with identifier `fi`, and Dutch with identifier `nl`.

If you add new languages to the built-in files, or create your own JSON files, be sure to check that the language identifiers used are listed in the [IANA language subtag registry](https://www.iana.org/assignments/language-subtag-registry).

When using more than two languages is not essential to explain how things work, examples below may contain just two languages.

### Letter case and punctuation in labels

Labels can use both uppercase and lowercase letters, and any mix of them. Toisto will check the answers to quizzes in a case sensitive manner.

Labels that contain complete sentences or utterances (for example, "Hello!") are written with an initial capital letter and with punctuation. Labels that contain individual words or phrases (for example, "days of the week") are not written with an initial capital, unless the first word is always written with a capital (for example, "I am"), and don't have punctuation.

### Labels with spelling variants

When there are multiple ways to spell a label, use the pipe symbol (`|`) to separate the alternatives. Toisto will only use the first of the alternatives to quiz the user, but will accept the other alternatives as answer.

```json
{
    "concepts": {
        "vegetable": {
            "singular": {
                "en": "vegetable",
                "nl": "de groente"
            },
            "plural": {
                "en": "vegetables",
                "nl": "de groenten|de groentes"
            }
        }
    }
}
```

To prevent having to spell out that "it's" is an alternative for "it is" in every label that contains "it is", Toisto has [builtin spelling variants](../src/languages/spelling_alternatives.json).

The builtin spelling alternatives are specified as a mapping from regular expressions to replacements, organized per language:

```json
{
    "en": {
        "\\bI am\\b": "I'm",
        "\\byou are\\b": "you're",
        "^You are\\b": "You're",
        "...": "..."
    },
    "fi": {
        "^[ms]inä ": "",
        " [ms]inä ": " ",
        "...": "..."
    },
    "nl": {
        "\\bjij\\b": "je",
        "^Jij\\b": "Je",
        "...": "..."
    }
}
```

> [!NOTE]
> Backslashes need to be escaped in the JSON file, hence the double backslashes.

Some spelling alternatives should only be applied if the language is the user's source language and not when the language is the user's target language. For example, users with Dutch as target language should learn nouns together with their article ("de" or "het"), but users with Dutch as source language should be allowed to omit them.

These spelling alternatives can be specified under the `<language identifier>-if-source-language` key:

```json
{
    "nl-if-source-language": {
        "^de ": "",
        "^het ": ""
    }
}
```

### Labels with spoken language

To indicate that a label is only used in spoken language, add an asterisk (`*`) to the end. Toisto will only quiz the label using speech.

```json
{
    "concepts": {
        "7": {
            "en": "seven",
            "fi": [
                "seitsemän",
                "seittemän*"
            ]
        }
    }
}
```

### Labels with notes

Sometimes labels are ambiguous. For example, "you" in English can mean both one or multiple persons. To help the user understand which meaning is intended, a note can be added to the label. The note is the part after the semicolon (`;`):

```json
{
    "concepts": {
        "to live": {
            "singular": {
                "first person": "...",
                "second person": {
                    "en": "you live;singular",
                    "nl": "jij woont"
                },
                "third person": "..."
            },
            "plural": {
                "first person": "...",
                "second person": {
                    "en": "you live;plural",
                    "nl": "jullie wonen"
                },
                "third person": "..."
            }
        }
    }
}
```

In the above example, Toisto will show the note to the user when asking for the Dutch translation of "you live".

It's also possible to add two notes. The first note will be shown as part of the quiz instruction. The second note will be shown after the user has answered. This can be used to point out extra information, for example:

```json
{
    "concepts": {
        "to live": {
            "singular": {
                "first person": "...",
                "second person": {
                    "en": "you live;singular;the second-person pronoun you is used for both the singular and the plural",
                    "nl": "jij woont"
                },
                "third person": "..."
            },
            "plural": {
                "first person": "...",
                "second person": {
                    "en": "you live;plural;the second-person pronoun you is used for both the singular and the plural",
                    "nl": "jullie wonen"
                },
                "third person": "..."
            }
        }
    }
}
```

If only the second note is needed, simply leave the first one empty:

```json
{
    "concepts": {
        "garlic": {
            "fi": "valkosipuli;;valko- ('white') + sipuli ('onion')"
        }
    }
}
```

### Concepts with multiple labels

Labels consist of either one string or a list of strings. A list of strings is used when there are multiple equivalent ways to express the concept in a language, as with "Mikä päivä tänään on?" and "Mikä päivä on tänään?" below. Toisto will quiz the user with each synonym, so in the example below users practicing Finnish will be asked to translate both Finnish sentences.

```json
{
    "concepts": {
        "what day is it today": {
            "en": "What day is it today?",
            "fi": [
                "Mikä päivä tänään on?",
                "Mikä päivä on tänään?"
            ]
        }
    }
}
```

### Concepts without label in some languages

Some concepts have a label in one language, but not in other languages. Mämmi, for example, is a traditional Finnish dessert, eaten around Eastern. There's no label in English or Dutch for mämmi. To allow Toisto to explain the meaning of mämmi when quizzing the user, specify it between brackets:

```json
{
    "concepts": {
        "mämmi": {
            "en": "(Traditional Finnish Easter dessert)",
            "fi": "mämmi"
        }
    }
}
```

### Multiple concepts with the same label

Sometimes a concept in one language can be two different concepts in another language. For example, both in English and Dutch there are separate greetings for the afternoon and the whole day: "Good afternoon" and "Good day" in English and "Goedemiddag" and "Goedendag" in Dutch. In Finnish "Hyvää päivää", or just "Päivää", is used for both. As an aside, "Hyvää iltapäivää", although grammatically correct, is not used.

If we would include all these labels in one concept, Toisto would consider "Goedemiddag" a correct translation of "Good day", which is undesirable. The solution is to have two concepts, one for "good afternoon" and one for "good day". Both concepts get the Finnish labels "Hyvää päivää" and "Päivää". The Finnish labels for the "good afternoon" concept get a note that Toisto shows when asking for the Dutch or English translation of "Hyvää päivää" or "Päivää" so that the user knows the context. The note is the part after the semicolon (`;`).

In the JSON file this looks as follows:

```json
{
    "concepts": {
        "good afternoon": {
            "en": "Good afternoon!",
            "fi": [
                "Hyvää päivää!;afternoon",
                "Päivää!;afternoon"
            ],
            "nl": "Goedemiddag!"
        },
        "good day": {
            "en": "Good day!",
            "fi": [
                "Hyvää päivää!",
                "Päivää!"
            ],
            "nl": "Goedendag!"
        }
    }
}
```

### Grammatical number

When concepts can have both singular and plural forms, such as with most nouns, these are represented in the JSON as mappings with `singular` and `plural` as keys and concepts as values.

The format of the JSON files is as follows:

```json
{
    "concepts": {
        "day": {
            "singular": {
                "en": "day",
                "fi": "päivä",
                "nl": "de dag"
            },
            "plural": {
                "en": "days",
                "fi": "päivät",
                "nl": "de dagen"
            }
        }
    }
}
```

### Diminutive

When a concept has a diminutive, the diminutive can be included in the JSON file by using `root` for the base form of the concept and `diminutive` for the diminutive form:

```json
{
    "concepts": {
        "table": {
            "root": {
                "nl": "de tafel"
            },
            "diminutive": {
                "nl": "het tafeltje"
            }
        }
    }
}
```

With the example above, Toisto will quiz users with Dutch as target language for the diminutive form of "de tafel".

Note that in many languages, diminutives can (also) be formed by using multi-word constructions such as "little table". Though possible, it is not recommended to add these to the JSON files because then Toisto will quiz both the translation of the multi-word construction as well as the diminutive form of the root, which seems superfluous. To help the user understand the meaning of the diminutive, include the multi-word construction as follows (see the section [Concepts without label in some languages](#concepts-without-label-in-some-languages) above):

```json
{
    "concepts": {
        "table": {
            "root": {
                "en": "table"
                "nl": "de tafel"
            },
            "diminutive": {
                "en": "(little table)",
                "nl": "het tafeltje"
            }
        }
    }
}
```

### Grammatical gender

When concepts have multiple genders, these can be specified as follows:

```json
{
    "concepts": {
        "parent": {
            "female": {
                "en": "mother",
                "nl": "de moeder"
            },
            "male": {
                "en": "father",
                "nl": "de vader"
            }
        }
    }
}
```

It is also possible to have a neutral gender:

```json
{
    "concepts": {
        "parent": {
            "female": {
                "en": "mother",
                "nl": "de moeder"
            },
            "male": {
                "en": "father",
                "nl": "de vader"
            },
            "neuter": {
                "en": "parent",
                "nl": "de ouder"
            }
        }
    }
}
```

Note that Toisto uses gender only for verbs at the moment, see the next section. The examples above are not in the built-in files.

### Grammatical person

When concepts, usually verbs and pronouns, have different persons, these are represented in the JSON as mappings with `first person`, `second person`, and `third person` as keys.

The format of the JSON files is as follows:

```json
{
    "concepts": {
        "to have": {
            "singular": {
                "first person": {
                    "en": "I have",
                    "nl": "ik heb"
                },
                "second person": {
                    "en": "you have;singular",
                    "nl": "jij hebt"
                },
                "third person": {
                    "female": {
                        "en": "she has",
                        "nl": "zij heeft"
                    },
                    "male": {
                        "en": "he has",
                        "nl": "hij heeft"
                    }
                }
            },
            "plural": {
                "first person": {
                    "en": "we have",
                    "nl": "wij hebben"
                },
                "second person": {
                    "en": "you have;plural",
                    "nl": "jullie hebben"
                },
                "third person": {
                    "en": "they have",
                    "nl": "zij hebben"
                }
            }
        }
    }
}
```

Note that because the second person singular and plural are the same in English, Toisto needs to tell the user whether it is asking for a translation of the singular version or the plural version of "You are". The note is the part after the semicolon (`;`).

Because Finnish does not distinguish between male and female gender, the third person singular of verbs in Finnish is included directly under the `third person` key:

```json
{
    "concepts": {
        "to have": {
            "singular": {
                "first person": "...",
                "second person": "...",
                "third person": {
                    "fi": "hänellä on",
                    "female": {
                        "en": "she has",
                        "nl": "zij heeft"
                    },
                    "male": {
                        "en": "he has",
                        "nl": "hij heeft"
                    }
                }
            },
            "plural": "..."
        }
    }
}
```

### Infinitive

When concepts are verbs, infinitives can be specified as follows:

```json
{
    "concepts": {
        "to have": {
            "infinitive": {
                "en": "to have",
                "fi": "olla (omistaa)"
            },
            "singular": {
                "first person": {
                    "en": "I have",
                    "fi": "minulla on"
                },
                "second person": "..."
            },
            "plural": "..."
        }
    }
}
```

### Tenses

When concepts are verbs, the present tense and the past tense can be specified as follows:

```json
{
    "concepts": {
        "to be": {
            "infinitive": "...",
            "present tense": {
                "singular": {
                    "first person": {
                        "en": "I am",
                        "fi": "minä olen",
                    },
                    "second person": "..."
                },
                "plural": "..."
            },
            "past tense": {
                "singular": {
                    "first person": {
                        "en": "I was",
                        "fi": "minä olin",
                    },
                    "second person": "..."
                },
                "plural": "..."
            }
        }
    }
}
```

### Degrees of comparison

Degrees of comparison are specified as follows:

```json
{
    "concepts": {
        "small": {
            "positive degree": {
                "en": "small",
                "nl": "klein"
            },
            "comparative degree": {
                "en": "smaller",
                "nl": "kleiner"
            },
            "superlative degree": {
                "en": "smallest",
                "nl": "kleinst"
            }
        }
    }
}
```

When there are synonyms, they need to be in the same order in every degree. This makes sure Toisto does not consider "suurin" a superlative of "iso".

```json
{
    "concepts": {
        "big": {
            "positive degree": {
                "en": "big",
                "fi": ["iso", "suuri"]
            },
            "comparative degree": {
                "en": "bigger",
                "fi": ["isompi", "suurempi"]
            },
            "superlative degree": {
                "en": "biggest",
                "fi": ["isoin", "suurin"]
            }
        }
    }
}
```

### Sentence forms

When the concept file contains both the declarative and the interrogative form of a sentence, Toisto can generate quizzes to change one into the other. Sentence forms are specified as follows:

```json
{
    "concepts": {
        "the car is black": {
            "declarative": {
                "en": "The car is black.",
                "nl": "De auto is zwart."
            },
            "interrogative": {
                "en": "Is the car black?",
                "nl": "Is de auto zwart?"
            }
        }
    }
}
```

### Grammatical polarity

Polarity (affirmative and negative sentence forms) can be specified as follows:

```json
{
    "concepts": {
        "the car is black": {
            "affirmative": {
                "en": "The car is black.",
                "nl": "De auto is zwart."
            },
            "negative": {
                "en": "The car is not black.",
                "nl": "De auto is niet zwart."
            }
        }
    }
}
```

### Numbers

Cardinal and ordinal numbers can be specified as follows:

```json
{
    "concepts": {
        "one": {
            "cardinal": {
                "en": "one",
                "fi": "yksi"
            },
            "ordinal": {
                "en": "first",
                "fi": "ensimmäinen"
            }
        }
    }
}
```

### Abbreviations

Abbreviations can be specified as follows:

```json
{
    "concepts": {
        "llc": {
            "full form": {
                "en": "limited liability company",
                "fi": "osakeyhtiö",
                "nl": "de naamloze vennootschap"
            },
            "abbreviation": {
                "en": "LLC",
                "fi": "oy",
                "nl": "de NV"
            }
        }
    }
}
```

### Concept relationships

#### Compound concepts

When a concept is a compound of one or more other concepts, this can be specified with the `roots` relation. Toisto will only quiz a *compound* concept when all *root* concepts have been quizzed. The `roots` relationship can be specified by adding a `roots` key to the concept with a list of concept identifiers as value:

```json
{
    "concepts": {
        "day": {
            "singular": {
                "en": "day",
                "nl": "de dag"
            },
            "plural": {
                "en": "days",
                "nl": "de dagen"
            }
        },
        "week": {
            "singular": {
                "en": "week",
                "nl": "de week"
            },
            "plural": {
                "en": "weeks",
                "nl": "de weken"
            }
        },
        "days of the week": {
            "roots": ["day", "week"],
            "en": "days of the week",
            "nl": "de dagen van de week"
        }
    }
}
```

If a concept has exactly one root, for example because not all roots have been included in the JSON files yet, the `roots` value can be a string instead of a list of concept identifiers.

If the root concepts differ per language, an object with languages as keys can be used:

```json
{
    "concepts": {
        "shirt": {
            "en": "shirt",
            "fi": "paita"
        },
        "sweater": {
            "roots": {
                "fi": "shirt"
            },
            "en": "sweater",
            "fi": "neulepaita"
        }
    }
}
```

If the plural of a compound word is easily derived from the plural of the last root, built-in JSON files may omit the plural of the compound word.

#### Antonyms

When one concept is an antonym (opposite) of another concept, this can be specified with the `antonym` relation. Toisto will add quizzes to ask users for the antonym of concepts in their target language.

```json
{
    "concepts": {
        "big": {
            "en": "big",
            "nl": "groot",
            "antonym": "small"
        },
        "small": {
            "en": "small",
            "nl": "klein",
            "antonym": "big"
        }
    }
}
```

If a concept has more than one antonym (for example, "large" and "big" are both antonyms of "small"), the `antonym` value can be a list of concept identifiers instead of a string.

#### Hypernyms

> [!NOTE]
> Concept X is a hypernym of concept Y if concept Y is a (kind of) X. For example, red is a color, so the concept "color" is a hypernym of the concept "red". The reverse relation is called hyponym, so "red" is a hyponym of "color".

When one concept is a hypernym of another concept (and conversely the other concept is a hyponym of the first concept), this can be specified with the `hypernym` relation. Toisto will derive the hyponym relations automatically. Toisto uses the hypernym and hyponym relations to decide which related concepts to use when a user selects a concept to practice. Given the JSON below, the command `toisto practice --concept color`, would select both color and red to practice.

```json
{
    "concepts": {
        "color": {
            "en": "color",
            "nl": "de kleur",
        },
        "red": {
            "hypernym": "color",
            "en": "red",
            "nl": "rood",
        }
    }
}
```

If a concept has more than one hypernym (for example, "pet" and "mammal" are both hypernyms of "dog"), the `hypernym` value can be a list of concept identifiers instead of a string.

#### Holonyms

> [!NOTE]
> Concept X is a holonym of concept Y if concept Y is a part of X. For example, cars have wheels, so the concept "car" is a holonym of the concept "wheel". The reverse relation is called meronym, so "wheel" is a meronym of "car".

When one concept is a holonym of another concept (and conversely the other concept is a meronym of the first concept), this can be specified with the `holonym` relation. Toisto will derive the meronym relations automatically. Toisto uses the holonym and meronym relations to decide which related concepts to use when a user selects a concept to practice. Given the JSON below, the command `toisto practice --concept car`, would select both the concept "car" and the concept "wheel" to practice.

```json
{
    "concepts": {
        "car": {
            "en": "car",
            "nl": "de auto",
        },
        "wheel": {
            "holonym": "car",
            "en": "wheel",
            "nl": "het wiel",
        }
    }
}
```

If a concept has more than one holonym (for example, "chair" and "table" are both holonyms of "leg"), the `holonym` value can be a list of concept identifiers instead of a string.

#### Concept involvement

When one concept involves another concept, this can be specified with the `involves` relation. Toisto will derive the inverse relation automatically. Toisto uses the involvement relations to decide with related concepts to use when a user selects a concept to practice. Given the JSON below, the command `toisto practice --concept "to paint"`, would select "to paint", "painter", and "painting" to practice.

```json
{
    "concepts": {
        "to paint": {
            "involves": [
                "painter",
                "painting"
            ],
            "en": "to paint",
            "nl": "schilderen",
        },
        "painter": {
            "en": "painter",
            "nl": "de schilder",
        },
        "painting": {
            "en": "painting",
            "nl": "het schilderij",
        }
    }
}
```

If a concept involves just one other concept (for example, "to save" involves only "money"), the `involves` value can be a single concept identifier instead of a list of concept identifiers.

#### Questions/answers

When one concept is a question and the other concept is the answer, this can be specified using the `answer` relation. Toisto will add a quiz, asking the user to answer the question in their target language.

```json
{
    "concepts": {
        "what do you like": {
            "en": "What do you like?;ice cream",
            "fi": "Mistä sinä pidät?;jäätelöä",
            "answer": "i like ice cream"
        },
        "i like ice cream": {
            "en": "I like ice cream.",
            "fi": "Minä pidän jäätelöstä.|Pidän jäätelöstä."
        }
    }
}
```

Answers are also possible if the concept has multiple grammatical forms, like singular and plural:

```json
{
    "concepts": {
        "what do you like": {
            "singular": {
                "en": "What do you like?;singular/ice cream",
                "fi": "Mistä sinä pidät?;jäätelöä"
            },
            "plural": {
                "en": "What do you like?;plural/ice cream",
                "fi": "Mistä te pidätte?;jäätelöä"
            },
            "answer": "i like ice cream"
        },
        "i like ice cream": {
            "singular": {
                "en": "I like ice cream.",
                "fi": "Minä pidän jäätelöstä.|Pidän jäätelöstä."
            },
            "plural": {
                "en": "We like ice cream.",
                "fi": "Me pidämme jäätelöstä.|Pidämme jäätelöstä."
            }
        }
    }
}
```

If a concept has multiple answers, the `answer` value can be a list of concept identifiers instead of a string:

```json
{
    "concepts": {
        "do you like ice cream": {
            "en": "Do you like ice cream?",
            "fi": "Pidätko sinä jäätelöstä?",
            "answer": [
                "yes, i like ice cream",
                "no, i don't like ice cream"
            ]
        },
        "yes, i like ice cream": {
            "answer-only": true,
            "en": "Yes, I do.",
            "fi": "Pidän."
        },
        "no, i don't like ice cream": {
            "answer-only": true,
            "en": "No, I don't.",
            "fi": "En."
        }
    }
}
```

The answer concepts in the previous example have the key `answer-only` set to `true`. This tells Toisto not to generate quizzes for these two concepts. Given how Finnish and English deal with answering yes/no questions differently, it doesn't make sense to ask users to, for example, translate "Yes, I do" into "Pidän".

## Quizzes

Toisto uses the concepts to generate quizzes. Currently, the following types of quizzes are generated:

1. Translate a concept from the target language to the source language.
2. Listen to a concept in the target language and then type in what was said.
3. Translate a concept from the source language to the target language.
4. Listen to a concept in the target language and then translate what was said in the source language.
5. Singularize a plural concept or pluralize a singular concept.
6. Diminutize a concept.
7. Change the person of a concept.
9. Change the gender of a concept.
9. Provide the positive, comparative, or superlative degree of comparison, given an adjective in another degree.
10. Change the tense of a concept between infinitive, present tense, and past tense.
11. Change the sentence form from declarative to interrogative and vice versa.
12. Change the polarity from affirmative to negative and vice versa.
13. Change cardinal numbers into ordinal numbers and vice versa.
14. Give the antonym.
15. Answer a question.
16. Abbreviate a concept or give the full-form of the abbreviation.

Except when asking the user to translate from the source language to the target language, quizzes only use the user's target language.

## Spaced repetition

Toisto uses a very simple implementation of a spaced repetition algorithm. Toisto does not make assumptions about how many concepts the user wants to practice per session or per day. It only keeps track of the retention of quizzes, i.e. how long the user has been correctly answering a quiz. Retention is defined as the time between the most recent correct answer and the oldest correct answer, where there have been no incorrect answers in between.

For example, if a user answers a quiz correctly on March 1, incorrectly on March 3, correctly on March 6, correctly on March 8, and correctly on March 15, that quiz has a retention of nine days (March 6 to March 15).

Each time a quiz is answered correctly, the quiz is silenced for a while. The longer the quiz's current retention, the longer the quiz is silenced. Whenever the user makes a mistake the retention is reset to zero.

If a user knows the correct answer the first time a quiz is presented, the quiz is silenced for a longer duration (24 hours).

## Progress savefile

When the program is stopped, progress is saved in a file named `.toisto-progress-{target language}.json` in the user's home folder, for example `.toisto-progress-fi.json`. So each target language gets its own progress file.

Each entry in the file is the progress of one specific quiz. The key denotes the quiz, the value contains information about the user's retention of the quiz. This looks as follows:

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
