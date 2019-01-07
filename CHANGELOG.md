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
### Added
- add U.S. grant funding acknowledgment to README
- include spec option that deactivates unused objective expression indices
- in the run experiment/trial scripts, start a script that moves the solution file to s3
- include new script that moves solution file to s3 after solving.  s3 for the win!
### Changed
- rename jupyter file names for better organization. Oh yeah.
- move graphic files out of the repository and into the local workspace
- improve log messaging from slurm scripts
### Fixed
- only load and resave model when conducting experiments if model is being modified
- fix the check for whether any model modifications were specified
- check whether Objective is 'indexed' Pyomo component when putting results into dictionary

## [0.0alpha1.dev4] -- 2018-12-01
### Added
- add manifest file to ensure configuration example, data, and version files are included in build
- add scripts for running optimization studies using SLURM workload manager on the AWS CBPO server, "Cloudfish"
- do the set-up for the config directory with a post-installation command in setup.py
- add example yaml specification files for batches, studies, experiments, and models
- set up new directory structure in bin/ for different kinds of 'run_specs'
- add sci-mode (pycharm) script to evaluate the model generation functionality
### Changed
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
### Fixed
- include files that were incorrectly being git-ignored
- use $USER variable to set ~/config output and logging directories
- add numpy, matplotlib, cloudpickle as installation requirements in seutp.py
- fix gitignore to stop ignoring files in bin/ directory
- use try block when checking VERSION for cases when packages are not 'installed'
- minor bug fixes
- fix path of saved model pickle, so that it's not on a compute node when running on AWS
- use Popen() instead of call() from subprocess so that SLURM jobs are allowed to continue running
### Removed
- remove unused shell script file 'run_slurm.sh'
- remove Jeeves attribute from Datahandler so it can be pickled with a smaller file size

## [0.0alpha1.dev3] -- 2018-10-23
### Added
- This release initializes the newly combined repository
(merging code originally generated in the "OptSandbox",
     "OptEfficiencySubProblem", and "CastJeeves" project repositories)
- add bash script to run efficiency model counties as a daemon process

### Changed
- moved jupyter notebook up from the efficiencysubproblem folder
to the project root level
- moved python and bash scripts to a project root level bin/ folder
- placed output, graphics, and log path specifications into a project
root level config/ folder

### Fixed
