# Changelog

All notable changes to Toisto will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v0.0.11 - unreleased

### Added

- When concepts have female and male versions add quizzes for changing the words into the opposite gender.

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
