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

[Current Development]

## [0.1b1] -- 2019-04-02
### Added
- efficiencysubproblem
    - expression is added to model for getting a single parcel's load
    - functions are added for inspecting a model 
- castjeeves
    - add method to convert between agencyid and agencyfullname
    - add method for getting sectors from loadsourceshortnames

### Changed
- general
    - updated the 2010 No Action Loads report being used    
        
### Fixed
- general
    - agencies other than 'Non-Federal' are dropped when getting the base loading table
- castjeeves
    - single column conversions' preserve order option using a left join.

## [0.1a1.dev6] -- 2019-03-31
### Added
- general
    - add control option for moving the CAST formatted solution table to s3
    - add input arguments to run scripts for setting a logging level
- efficiencysubproblem
    - expressions are added to model for more detailed investigation of loads
- castjeeves
    - single column converts now have an option to preserve order of the input table    
    
### Changed
- general
    - move-to-s3 options are combined into one key for specification files
    - solution table acre values are now rounded to a single decimal point
    - slurm 'ntasks' and 'ntasks-per-node' values are reduced to 32 to ease processing
    - log formatting configuration file is now in yaml style  

### Fixed
- general
    - study script is now exited early if model generation raises an error
    - a sparse solution table is now generated even when solution is not feasible

## [0.1a1.dev5] -- 2019-03-21
### Added
- general
    - add U.S. grant funding acknowledgment to README
    - include spec option that deactivates unused objective expression indices
    - in the run experiment/trial scripts, start a script that moves the solution file to s3
    - include new script that moves solution file to s3 after solving.  s3 for the win!
    - add directory for control files from batch, study, experiment, and trials
    - add ability/option to translate solution table to CAST BMP-input file format
    - allow for list type in geography_entities string matching for batch specifications
- efficiencysubproblem
    - add modify_model method that will do specified experiment setup actions
    - include 'results' in solution dictionary from a basic solve
- castjeeves
    - add method to convert bmp shortnames to fullnames

### Changed
- general
    - rename jupyter file names for better organization. Oh yeah.
    - move graphic files out of the repository and into the local workspace
    - improve log messaging from slurm scripts
    - use castjeeves to parse geography entities from the batch specification
    - rename run_scripts with 'step[#]' to clarify order
    - make it so that a control file grows from each later step
    - move study specifications into the batch specs, instead of having separate files  

### Fixed
- general
    - only load and resave model when conducting experiments if model is being modified
    - fix the check for whether any model modifications were specified
    - check whether Objective is 'indexed' Pyomo component when putting results into dictionary
    - fix the slurm run process, so srun commands are not calling other srun commands

## [0.1a1.dev4] -- 2018-12-01
### Added
- general
    - add manifest file to ensure configuration example, data, and version files are included in build
    - add scripts for running optimization studies using SLURM workload manager on the AWS CBPO server, "Cloudfish"
    - do the set-up for the config directory with a post-installation command in setup.py
    - add example yaml specification files for batches, studies, experiments, and models
    - set up new directory structure in bin/ for different kinds of 'run_specs'
    - add sci-mode (pycharm) script to evaluate the model generation functionality
- efficiencysubproblem
    - add matplotlib function in vis module for plotting load reduction curve
    - add text to 'doc' arguments for model components
    - add 'backend' argument to plotting methods
    - add module with functions to read yaml specification files
    - add model_generator, expressions, and components to replace modelhandler
    - add utils.py file to model handling module

### Changed
- general
    - set filepath configurations from within a new config/ directory
    - move jupyter notebooks into bin/ directory
    - updated and improved README documentation
    - reorganize bayota_settings package with a 'base' and 'install_config' module
    - get filepath specifications in the bayota_settings package
    - set log formatting in bayota_settings package
    - rename and reorganize command line interface code
    - move csv files to top-level dir so they are not installed with packages
    - move path specifications out of packages and into the config
    - put version number in separate top-level file that is read using pkg_resources
    - change pathing to use a 'bayota workspace' separate from the git repository
    - separate the model generation step from the other run scripts
    - exclude geography text from study spec names, since that is now in separate geography specs
- efficiencysubproblem
    - add offending value string to error message in datahandler for unacceptable objectives or geographies
    - updated test methods for Study class
    - use separately-defined Pyomo Expression components to build model instances
    - move solving methods to top of solvehandler (out of SolveHandler class)

### Fixed
- general
    - include files that were incorrectly being git-ignored
    - use $USER variable to set ~/config output and logging directories
    - add numpy, matplotlib, cloudpickle as installation requirements in seutp.py
    - fix gitignore to stop ignoring files in bin/ directory
    - use try block when checking VERSION for cases when packages are not 'installed'
    - minor bug fixes
    - fix path of saved model pickle, so that it's not on a compute node when running on AWS
    - use Popen() instead of call() from subprocess so that SLURM jobs are allowed to continue running
- efficiencysubproblem
    - check infeasible constraints only if solver termination condition is 'not feasible'
- castjeeves
    - temp directory is now created if it doesn't exist

### Removed
- general
    - remove unused shell script file 'run_slurm.sh'
    - remove Jeeves attribute from Datahandler so it can be pickled with a smaller file size
- efficiencysubproblem
    - remove multirun attribute variable from Study class

## [0.1a1.dev3] -- 2018-10-23
### Added
- general
    - This release initializes the newly combined repository
    (merging code originally generated in the "OptSandbox",
         "OptEfficiencySubProblem", and "CastJeeves" project repositories)
    - add bash script to run efficiency model counties as a daemon process
- efficiencysubproblem
    - git source control to this project under 'BayOTA'
    - renamed top folder from 'OptSandbox' to 'sandbox'
    - top-level definitions file to specify root directory paths
    - error raised for unrecognized objective type passed to Study class
    - test cases for load reduction objective problem
    - included file print level keyword parameter for Study class
- sandbox
    - Ability to recognize running on AWS, and if so, read/write to s3
    - Reorder the CAST-input table headers priot to writing to file
    - Add ScenarioName column to CAST-input tables when lhs sampling
- castjeeves
    - include config file in castjeeves directory

### Changed
- general
    - moved jupyter notebook up from the efficiencysubproblem folder
    to the project root level
    - moved python and bash scripts to a project root level bin/ folder
    - placed output, graphics, and log path specifications into a project
    root level config/ folder
- efficiencysubproblem
    - merged into a monorepo with 'castjeeves' and 'sandbox'
    - reorganized data handler classes for more flexible inheritance of new types
    - updated the the return of Study.go methods to include solution objective value
    - restructured data handling and model handling to use mixin inheritance pattern, thus
    eliminating the duplication of code for each type of objective/geoscale combination.
    - output now piped through python logging module instead of print() statements
- sandbox
    - merged into a monorepo with 'efficiencysubproblem' and 'sandbox'
    - renamed top folder from 'OptSandbox' to 'sandbox'
    - Use Dry Tons as units for manure transport instead of percent
- castjeeves
    - merged into a monorepo with 'efficiencysubproblem' and 'sandbox'
    - renamed Metadata sourcehook class name to 'Meta'
    - renamed sourcehook to 'meta' and jeeves attribute to 'metadata_tables'

### Fixed
- efficiencysubproblem
    - updated import paths
    - resolved filenotfound error with ouput directory
    - add posix path check in setup.py for windows OS
- sandbox
    - Methods that append bmps to the decision space tables
    - Use appropriate Base Condition (from year and name metadata info)
    - add posix path check in setup.py for windows OS
- castjeeves
    - brought sourcehooks up-to-date w/changes missed during merges
    - replaced '' with np.nan for out-of-the-watershed transport
    - removed docs folder in castjeeves that was a duplicate of sandbox docs
    - add posix path check in setup.py for windows OS

## [0.1a1.dev2] -- 2018-09-14
### Added
- general
    - This changelog.md file
- sandbox
    - Ability to generate scenarios with a latin hypercube sampling method
    - Two data subdirectories for holding the source and metadata .csv files
- castjeeves
    - included yaml file for Gitlab CI testing
    - added pytest-cov to test runner to generate coverage report

### Changed
- sandbox
    - improved application structure for better stability and maintenance
    - Use .csv files loaded from the CAST SQL Server database instead
    of the .xlsx files from CAST website.
- castjeeves
    - switched testing utility to pytest
    - changed license to GNUGPLv3.0

### Fixed
- sandbox
    - Included TblBmpCategory.csv in directory with source data

### Removed
- sandbox
    - unnecessary TblQuery modules
- castjeeves
    - removed usage/dependency of 'tqdm' package

## [0.1a1.dev1] -- 2018-01-05
### Added
- sandbox
    - git source control to this project
- castjeeves
    - git source control to this project
