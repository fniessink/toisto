# Changelog

All notable changes to Toisto will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v0.2.0 - 2022-11-27

### Added

- It is possible to specify usage relations between concepts in topic files. For example, the concept "days of the week" uses the concepts "day" and "week". Toisto will first quiz the user on "day" and "week" before quizzing "days of the week". Plural concepts automatically "use" singular concepts so that plural forms of concepts are quizzed before their singular form.
- When the quiz type is not "translate", as a reminder, show the meaning of the quizzed concept in the user's language after the quiz is finished. Closes [#31](https://github.com/fniessink/toisto/issues/31).
- Add more concepts to the house and nature topics and add an animals topic.
- Use Google Translate for text-to-speech, but fall back to the MacOS say command if getting the audio from Google Translate fails.

## v0.1.0 - 2022-11-20

### Changed

- Determine the time to silence a quiz using the retention so far, instead of the streak. Unfortunately, this is a backwards incompatible change and progress information is lost.
- Silence quizzes that the user knows on the first attempt for 24 hours.

### Added

- Add more concepts to the city, family, furniture, house, nature, and time topics.

## v0.0.16 - 2022-11-14

### Fixed

- For some streak lengths, Toisto would not give the correct duration for which the quiz will be silenced.

### Added

- Show until when a quiz is silenced in the progress table.
- Add listening-only quizzes. Closes [#43](https://github.com/fniessink/toisto/issues/43).

## v0.0.15 - 2022-11-08

### Fixed

- Fix the Dutch label for "shortest" in the degrees of comparison topic.

### Added

- When selecting new quizzes for the user to answer, do so in the order of topics and order of concepts in the topic files. This makes sure the user will be quizzed on concepts and topics concepts they have already been working on, before being introduced to new concepts and topics. Closes [#32](https://github.com/fniessink/toisto/issues/32).

## v0.0.14 - 2022-11-06

### Fixed

- Answers shown in "Another correct answer is..." would include the hint.

## v0.0.13 - 2022-11-06

### Fixed

- On MacOS Ventura, the say command that Toisto uses for speech does not print the spoken text, even when told to. Work-around the issue by having Toisto print the question itself.
- The plural of one synonym should not be accepted as the plural of another synonym and vice versa. For example, kauppakeskus and ostoskeskus both mean shopping centre, but the plural of kauppakeskus, kauppakeskukset, should still not be accepted as plural for ostoskeskus and vice versa. Fixes [#13](https://github.com/fniessink/toisto/issues/13).

### Added

- Added more words and sentences to the days, time, family, and greetings topics.
- Allow for specifying hints, for example to tell users to interpret "You are" as either singular or plural.

### Changed

- To not overwhelm the user with new quizzes, give preference to quizzes the user has seen before when selecting the next quiz.

## v0.0.12 - 2022-10-30

### Added

- Added a nature topic.
- Added shopping center to the city topic.
- Added quizzes for degrees of comparison and a topic with degrees of comparison.
- Added quizzes for grammatical person (first, second, and third person) and a topic with the verbs "to be" and "to have".

## v0.0.11 - 2022-10-27

### Added

- When concepts have female and male versions add quizzes for changing the words into the opposite gender (daughter-son, father-mother, etc.).

## v0.0.10 - 2022-10-25

### Added

- Added a possessive adjectives topic (my cat, your house, their cats, etc.).

## v0.0.9 - 2022-10-25

### Fixed

- Fixed typo in bibliotheken (city topic).

## v0.0.8 - 2022-10-23

- Added more phrases to the greetings topic.
- Added a city topic.

## v0.0.7 - 2022-10-21

### Fixed

- The food topic wouldn't work with languages other than Finnish.

## v0.0.6 - 2022-10-21

### Changed

- Renamed decks to topics. This also means the command line interface option `-d/--deck` was renamed to `-t/--topic`.

### Added

- Added a food topic.
- In addition to using builtin topic files, allow the user to load their own local topic files, using the command line interface option `-f/--topic-file`.

## v0.0.5 - 2022-10-18

### Added

- Add English as supported language.

## v0.0.4 - 2022-10-17

### Fixed

- Toisto did not start because the rich library was not bundled.

## v0.0.3 - 2022-10-17

### Added

- Added decks with words related to furniture and houses.
- Add command to show progress (`toisto {language} progress`).
- When the user translates a word correctly and there are multiple correct translations, also show the other translations.
- When words have a singular and plural version add quizzes for pluralizing and singularizing the words.
- When the user answers incorrectly, give them a chance to correct typo's.

## v0.0.2 - 2022-10-10

### Added

- Added a deck with colors and a deck with family related words.
- Added command line options for help, version, and specifying decks to use. Run `toisto -h` to see the help information.
- Entries in decks can have multiple answers.
- When the user translates words correctly multiple times in a row, silence the word for a while. The more often a word is correctly translated, the longer it is silenced.

### Fixed

- Some words in the decks included invisible white space, causing Toisto to never see the user's input as correct.

## v0.0.1 - 2022-10-05

- Initial version.
