# Overview

"BayOTA" (Bay Optimization Tools for Analysis) is a repository of
optimization and analysis tools created to serve the
Chesapeake Bay Program (CBP) Partners.
Specifically, these tools are designed to help users of CAST
(the Chesapeake Bay Assessement Scenario Tool), which
is the CBP Phase 6 time-averaged watershed model,
as part of the Optimization Tool Development Project
(EPA-R3-CBP-16-03).

* Version 0.0.1

This README documents steps necessary to get the
application up and running.

# Directory Structure

```
bayota
│
├── README.md              <- Top-level README for users/developers of this project.
├── CHANGELOG.md           <- Documentation of notable changes to this project
│
├── bin                    <- scripts (python, bash, slurm) for running from the command-line
│   └── ...
│
├── config                 <- specification of data output, graphics, and logging directory paths
│   └── ...
│
├── castjeeves             <- PACKAGE to access, query, and parse source data from the Chesapeake Bay Assessement Scenario Tool (CAST)
│   ├── __init__.py
│   └── ...
│
├── efficiencysubproblem   <- PACKAGE to solve optimization problem involving 'Efficiency' Best Management Practices (BMPs) of CAST
│   ├── __init__.py
│   └── ...
│
├── sandbox                <- PACKAGE for automated generation of valid BMP input files for use with CAST
│   ├── __init__.py
│   └── ...
│
├── jnotebooks             <- Jupyter notebooks for browser-based analyses
│   └── ...
│
├── util                   <- PACKAGE for utility methods that haven't yet found a home elsewhere
│   ├── __init__.py
│   └── ...
│
├── setup.py
├── MANIFEST.in
├── Dockerfile_36
└── LICENSE
```


# How do I get set up?


Get the latest version.
From the /bayota directory, run

    > git pull


### Install


**To install as a python package**

From the project root dir (bayota), enter:

    > python setup.py install

* Summary of set up
* Configuration
* Dependencies
* Database configuration
* Deployment instructions

#### Run the tests

    > python setup.py test

# Usage

To run the standard bash script:

    > cd bin/
    > chmod 755 bayota
    > chmod 755 bayota_efficiency.py

    # back up to the project root (bayota/)
    > cd ..

    # run the script (and you can include --daemon argument to detach process and run with no hangup)
    > ./bin/bayota

From the python prompt or in a jupyter notebook:

    >>> from efficiencysubproblem.src.study import Study

    # Create a model instance
    >>> s = Study(objectivetype='costmin', geoscale='county', geoentities=['Adams, PA'])

    # Solve the instance and get results
    >>> solveroutpath, csvpath, df, objective, feasible = s.go(constraint=5)


# How do I uninstall?

##### 1. To remove only the files created by "python setup.py install":

    > python setup.py clean

##### 2. To remove the installed package files from your environment (site-packages):

    > python setup.py develop --uninstall

##### 2. To remove everything

    > python setup.py develop --uninstall
    > rm -r bayota

# Who do I talk to? ###

* The U.S. EPA Chesapeake Bay Program
* Daniel E. Kaufman: dkaufman@chesapeakebay.net