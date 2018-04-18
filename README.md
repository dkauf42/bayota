# Overview

"OptSandbox" is an optimization application developed for
the Chesapeake Bay Assessement Scenario Tool (CAST)

* Version 0.2.0
* This release adapts the data queries to use csv tables
    generated from the CAST SQL Server.

This README documents the steps necessary to get the "OptSandbox"
application up and running.

## Usage

###### A simple example:

```python
python sandboxer.py
```

###### Help is available by using the "-h" parameter:

```python
python sandboxer.py -h
```

###### Example test cases are available by using the "-t" parameter:

```python
python sandboxer.py -t 1
```

Note:
There are three test cases available, and
no GUI appears when running a test case.

## How do I get set up?

It is recommended to follow this order:
1) run install from the setup file to configure
the python environment with necessary dependencies
2) run unittests (see below) to ensure proper functioning
3) run desired optimization experiments

#### Install

    > python setup.py install


* Summary of set up
* Configuration
* Dependencies
* Database configuration
* Deployment instructions

#### Run the unittests

    > python setup.py test

unittests are located in the subdirectory 'test', and test the following units:
* sandboxer.main()
* sandbox.util.OptCase
* sandbox.tables.TblJeeves

#### Run custom optimization experiments

    > python sandboxer.py

When running the software with no arguments,
a GUI appears that allows specifiation of geography and other metadata.

## How do I uninstall?

##### 1. To remove only the files created by "python setup.py install":

    > python setup.py clean

##### 2. To remove everything, delete the directory.

## Who do I talk to? ###

* The U.S. EPA Chesapeake Bay Program
* Daniel E. Kaufman: dkaufman@chesapeakebay.net