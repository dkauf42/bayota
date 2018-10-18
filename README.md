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
├── README.md              <- The top-level README for developers using this project.
│
├── castjeeves             <- Project to access, query, and parse source data from the Chesapeake Bay Assessement Scenario Tool (CAST)
│   └── ...
│
├── efficiencysubproblem   <- Project to solve optimization problem involving 'Efficiency' Best Management Practices (BMPs) of CAST
│   └── ...
│
├── sandbox                <- Project for automated generation of valid BMP input files for use with CAST
│   └── ...
│
├── jnotebooks             <- Jupyter notebooks for interactively accessing and running the bayota projects
│   └── ...
│
├── definitions.py         <- Specifies top-level directory information
│
├── CHANGELOG.md           <- Documentation of notable changes to this project
└── LICENSE
```


# How do I get set up?

**Each project is located in its own subdir:**
'castjeeves', 'efficiencysubproblem', 'sandbox'

Set up should be done for each project individually...


### Install

* Summary of set up
* Configuration
* Dependencies
* Database configuration
* Deployment instructions

#### Run the tests

    > python <subdir>/setup.py test

# Usage

# How do I uninstall?

##### 1. To remove only the files created by "python setup.py install":

    > python <subdir>/setup.py clean

##### 2. To remove everything, delete the directory.

# Who do I talk to? ###

* The U.S. EPA Chesapeake Bay Program
* Daniel E. Kaufman: dkaufman@chesapeakebay.net