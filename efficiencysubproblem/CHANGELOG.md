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

## Current Development
### Added
### Changed
### Fixed

## v0.0.1-alpha.0.3 - 2018-10-23
### Added
- git source control to this project under 'BayOTA'
- renamed top folder from 'OptSandbox' to 'sandbox'
- top-level definitions file to specify root directory paths
- error raised for unrecognized objective type passed to Study class
- test cases for load reduction objective problem
- included file print level keyword parameter for Study class

### Changed
- merged into a monorepo with 'castjeeves' and 'sandbox'
- reorganized data handler classes for more flexible inheritance of new types
- updated the the return of Study.go methods to include solution objective value
- restructured data handling and model handling to use mixin inheritance pattern, thus
eliminating the duplication of code for each type of objective/geoscale combination.
- output now piped through python logging module instead of print() statements

### Fixed
- updated import paths
- resolved filenotfound error with ouput directory
- add posix path check in setup.py for windows OS
