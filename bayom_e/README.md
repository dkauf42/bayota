# Overview

"bayom_e" is an optimization modeling toolbox
designed to support decision making when using
CAST (the Chesapeake Bay Assessement Scenario Tool), which
is the Chesapeake Bay Program's (CBP) Phase 6 time-averaged watershed model 

<br>

This README will document the steps necessary to get the optimization model
up and running.

# 📁 Directory Structure

```
├── README.md              <- The top-level README for developers using this project.
│
├── src                    <- Source code for use in this project.
│   ├── __init__.py        <- Makes src a Python module
│   │
│   ├── data_handling      <- Code to populate necessary source data
│   │   ├── interface.py
│   │   ├── datahandler_base.py
│   │   ├── dataloader_constraint_mixins.py
│   │   └── dataloader_geography_mixins.py
│   │
│   ├── model_handlers     <- Formulations of the optimization model
│   │   ├── interface.py
│   │   ├── modelhandler_base.py
│   │   ├── efficiencymodel_objective_mixins.py
│   │   └── efficiencymodel_geography_mixins.py
│   │
│   ├── solution_handling  <- Code to parse and manipulate run solutions
│   │   ├── ipopt_parser.py
│   │   └── solutionhandler.py
│   │
│   ├── solver_handling    <- Scripts to send commands to solver
│   │   ├── gjh_wrapper.py
│   │   └── solvehandler.py
│   │
│   ├── tests              <- Scripts to test and validate code using pytest
│   │   ├── test_datahandling.py
│   │   └── test_modelhandling.py
│   │
│   └── vis                <- Scripts to create exploratory and results oriented visualizations
│       ├── acres_bars.py
│       ├── acres_heatmap.py
│       ├── genericvis.py
│       ├── sequence_plot.py
│       └── zL_bars.py
│
├── CHANGELOG.md
├── MANIFEST.in
└── LICENSE
```

# ⚙ How do I get set up?

### Install

###### Note: The Ipopt solver must be installed/compiled separately in order to solve Efficiency BMP optimization problems.
- Instructions can be found at https://www.coin-or.org/Ipopt/documentation/node14.html
- After installation, the Ipopt executable location must be added to the environment $PATH variable


To be determined...
* Commands
* Summary of set up
* Configuration
* Dependencies
* Database configuration
* Deployment instructions

#### Run the unittests

>> python setup.py test

# ▶ Usage

To be determined...
###### A simple example (to run using GUI):


# commands

To be determined...

## 🗣️ Who do I talk to?

* The U.S. EPA Chesapeake Bay Program
* Daniel E. Kaufman: dkaufman@chesapeakebay.net