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
├── README.md              <- The top-level README for developers using this project.
│
├── data
│   ├── instance_data      <- Intermediate data that has been transformed.
│   └── raw                <- Original, immutable data.
│
├── jnotebooks             <- Notebooks for looking at model results and analyses
│
├── castjeeves             <- Submodule to query source data
│
├── src                    <- Source code for use in this project.
│   ├── __init__.py        <- Makes src a Python module
│   ├── study.py           <- Main class for setting up optimization runs
│   │
│   ├── data_handlers      <- Code to populate necessary source data
│   │   ├── county.py
│   │   ├── dataloader.py
│   │   └── lrseg.py
│   │
│   ├── model_handlers     <- Formulations of the optimization model
│   │   ├── costobjective_county.py
│   │   ├── costobjective_lrseg.py
│   │   ├── loadobjective_county.py
│   │   └── loadobjective_lrseg.py
│   │
│   ├── solution_handlers  <- Code to parse and manipulate run solutions
│   │   ├── ipopt_parser.py
│   │   └── solution_wrangler.py
│   │
│   ├── solver_handlers    <- Scripts to send commands to solver
│   │   ├── gjh_wrapper.py
│   │   └── solve_triggerer.py
│   │
│   ├── tests              <- Scripts to test and validate code using pytest
│   │   └── test_study.py
│   │
│   └── vis                <- Scripts to create exploratory and results oriented visualizations
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