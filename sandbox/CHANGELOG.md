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

## [0.0a1.dev4] -- 2018-12-01
### Added
### Changed
### Fixed

## [0.0a1.dev3] -- 2018-10-23
### Added
- Ability to recognize running on AWS, and if so, read/write to s3
- Reorder the CAST-input table headers priot to writing to file
- Add ScenarioName column to CAST-input tables when lhs sampling

### Changed
- merged into a monorepo with 'efficiencysubproblem' and 'sandbox'
- renamed top folder from 'OptSandbox' to 'sandbox'
- Use Dry Tons as units for manure transport instead of percent

### Fixed
- Methods that append bmps to the decision space tables
- Use appropriate Base Condition (from year and name metadata info)
- add posix path check in setup.py for windows OS

## [0.0a1.dev2] -- 2018-09-14
### Added
- Ability to generate scenarios with a latin hypercube sampling method
- This changelog.md file
- Two data subdirectories for holding the source and metadata .csv files

### Changed
- improved application structure for better stability and maintenance
- Use .csv files loaded from the CAST SQL Server database instead
of the .xlsx files from CAST website.

### Fixed
- Included TblBmpCategory.csv in directory with source data

### Removed
- unnecessary TblQuery modules

## [0.0a1.dev1] -- 2018-01-05
### Added
- git source control to this project