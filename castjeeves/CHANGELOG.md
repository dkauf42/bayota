# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)

Each version should:
- List its release date.
- Group changes to describe their impact on the project, as follows:
*Added* for new features.
*Changed* for changes in existing functionality.
*Deprecated* for once-stable features removed in upcoming releases.
*Removed* for deprecated features removed in this release.
*Fixed* for any bug fixes.
*Security* to invite users to upgrade in case of vulnerabilities.

### [Current Development]
#### Added
#### Changed
#### Fixed

## [0.0a1.dev4] -- 2018-12-01
#### Added
#### Changed
#### Fixed
- temp directory is now created if it doesn't exist

## [0.0a1.dev3] -- 2018-10-23
#### Added
- include config file in castjeeves directory

#### Changed
- merged into a monorepo with 'efficiencysubproblem' and 'sandbox'
- renamed Metadata sourcehook class name to 'Meta'
- renamed sourcehook to 'meta' and jeeves attribute to 'metadata_tables'

#### Fixed
- brought sourcehooks up-to-date w/changes missed during merges
- replaced '' with np.nan for out-of-the-watershed transport
- removed docs folder in castjeeves that was a duplicate of sandbox docs
- add posix path check in setup.py for windows OS

## [0.0a1.dev2] -- 2018-09-14
#### Added
- included yaml file for Gitlab CI testing
- added pytest-cov to test runner to generate coverage report

#### Changed
- switched testing utility to pytest
- changed license to GNUGPLv3.0

#### Removed
- removed usage/dependency of 'tqdm' package


## [0.0a1.dev1] -- 2018-01-05
#### Added
- git source control to this project