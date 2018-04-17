# README #

This README documents the steps necessary to get this application
up and running.

# Overview
"OptSandbox" is an optimization application developed for
the Chesapeake Bay Assessement Scenario Tool (CAST)

* Version 0.2.0
* This release adapts the data queries to use csv tables
    generated from the CAST SQL Server.

## Usage

A simple example:

```python
python sandboxer.py
```

## How do I get set up?

It is recommended to follow this order:
1) run install from the setup file to configure
the python environment with necessary dependencies
2) run unittests (see below) to ensure proper functioning
3) run optimization test case
4) run desired optimization experiments

### Installing

    > python setup.py install


* Summary of set up
* Configuration
* Dependencies
* Database configuration
* Deployment instructions

### Running the unittests

    > python setup.py test

unittests are located in the subdirectory 'test', and test the following units:
* sandboxer.main()
* sandbox.util.OptCase
* sandbox.tables.TblJeeves

### Running an optimization test case

    > python sandboxer.py -t 1

Test case #1 generates CAST scenarios for the county of Adams, PA.

Note: no GUI appears when running the test case.

### Running custom optimization experiments

    > python sandboxer.py

When running the software with no arguments,
a GUI appears that allows specifiation of geography and other metadata.

## Who do I talk to? ###

* The U.S. EPA Chesapeake Bay Program
* Daniel E. Kaufman: dkaufman@chesapeakebay.net