# Overview

"OptEfficiencySubProblem" is an optimization modeling toolbox
designed to support decision making when using
CAST (the Chesapeake Bay Assessement Scenario Tool), which
is the Chesapeake Bay Program's (CBP) Phase 6 time-averaged watershed model 

* Version Alpha
* This release is undergoing continual development to reach a Beta version

This README will document the steps necessary to get the optimization model
up and running.

# Directory Structure

```
├── README.md          <- The top-level README for developers using this project.
│
├── data
│   ├── instance_data  <- Intermediate data that has been transformed.
│   └── raw            <- Original, immutable data.
│
├── jnotebooks         <- Notebooks for looking at model results and analyses
│
├── src                <- Source code for use in this project.
│   ├── __init__.py    <- Makes src a Python module
│   │
│   ├── ipopt          <- Scripts specific to the Ipopt solver
│   │   └── ipopt_parser.py
│   │
│   ├── model_runners  <- Scripts to solve specific model configurations
│   │   └── singlerun.py
│   │
│   ├── models         <- Formulations of the optimization model
│   │   ├── costobjective.py
│   │   ├── costobjective_county.py
│   │   ├── loadobjective.py
│   │   └── loadobjective_county.py
│   │
│   └── vis            <- Scripts to create exploratory and results oriented visualizations
│       ├── acres_bars.py
│       ├── acres_heatmap.py
│       ├── genericvis.py
│       ├── sequence_plot.py
│       └── zL_bars.py
│
└── LICENSE
```

# How do I get set up?

### Install

To be determined...
* Commands
* Summary of set up
* Configuration
* Dependencies
* Database configuration
* Deployment instructions

#### Run the unittests

To be determined...

# Usage

To be determined...
###### A simple example (to run using GUI):


# How do I uninstall?

To be determined...

# commands

To be determined...
##### 2. To remove everything, delete the directory.

# Who do I talk to? ###

* The U.S. EPA Chesapeake Bay Program
* Daniel E. Kaufman: dkaufman@chesapeakebay.net