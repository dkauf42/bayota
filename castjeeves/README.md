# Overview

"CastJeeves" is a package that provides functionality for
accessing, querying, and parsing the source data from CAST 
(the Chesapeake Assessement Scenario Tool),
which is the CBP Phase 6 time-averaged watershed model.

This README documents the steps necessary to get "CastJeeves"
 up and running.

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

###### A minimal working example:

    > from castjeeves.src.jeeves import Jeeves
    > cj = Jeeves()
    > print(cj.geo.all_geotypes())

# How do I uninstall?

##### 1. To remove only the files created by "python setup.py install":

    > python setup.py clean

##### 2. To remove everything, delete the directory.

# Who do I talk to? ###

* The U.S. EPA Chesapeake Bay Program
* Daniel E. Kaufman: dkaufman@chesapeakebay.net