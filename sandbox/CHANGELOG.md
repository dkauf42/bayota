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

## [Current Development]
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

## [0.3.0] - 2018-04-27
### Added
- Ability to generate scenarios with a latin hypercube sampling method

### Changed
- improved application structure for better stability and maintenance

### Fixed
- Included TblBmpCategory.csv in directory with source data

## [0.2.0] - 2018-04-18
### Added
- This changelog.md file
- Two data subdirectories for holding the source and metadata .csv files

### Changed
- Use .csv files loaded from the CAST SQL Server database instead
of the .xlsx files from CAST website.

### Removed
- unnecessary TblQuery modules

## [0.1.0] - 2018-01-05
### Added
- git source control to this project