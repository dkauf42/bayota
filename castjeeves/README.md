# Overview

"CastJeeves" is a utility class with methods for
accessing, querying, and parsing source data from
the Chesapeake Bay Assessement Scenario Tool (CAST)

* Version 0.0.2
* This release initializes the repository
    (from code originally in the "sandbox" project)

This README documents the steps necessary to get the "CastJeeves"
application up and running.

# How do I get set up?

### Install

    > python setup.py install


* Summary of set up
* Configuration
* Dependencies
* Database configuration
* Deployment instructions

#### Run the unittests

# Usage

###### A simple example (to run using GUI):

    > from CastJeeves.jeeves import Jeeves
    > cj = Jeeves()
    > print(cj.geo.all_geotypes())

# How do I uninstall?

##### 1. To remove only the files created by "python setup.py install":

    > python setup.py clean

##### 2. To remove everything, delete the directory.

# Who do I talk to? ###

* The U.S. EPA Chesapeake Bay Program
* Daniel E. Kaufman: dkaufman@chesapeakebay.net