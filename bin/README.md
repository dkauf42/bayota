# Conducting optimization studies from this bin directory

***Note*** *This readme does not describe how to set up, install, or uninstall the BayOTA packages.\
For those instructions, please see the project-level guide: `bayota/README.md`*


This README documents how to conduct optimization studies using the BayOTA packages.

<details>
 <summary><strong>Table of Contents</strong> (click to expand)</summary>

* [Bin structure](#-bin-structure)
* [Usage](#-usage)
* [Troubleshooting & debugging](#-troubleshooting--debugging)
* [Who do I talk to?](#-who-do-i-talk-to)
</details>

# 📁 Bin Structure

In this bin directory, you will find:

* shell scripts
* jupyter notebooks
* python scripts
<br><br/>
* config files that specify optimization study parameters
*

#### Directory Tree
```
bin
│
├── README.md              <- README describing how to conduct optimization studies
│
├── cli                    <- command line interfaces written in python
│   └── ...
│
├── jnotebooks             <- jupyter notebooks for easy access to optimization studies and results analyses.
│   └── ...
│
├── python_scripts         <- python scripts for easy access to optimization studies and results analyses.
│   └── ...
│
├── shell_scripts          <- scripts for batch optimization studies.
│   └── ...
│
├── studies                <- .ini files that allow detailed specification of study parameters
│   └── ...
│
```


# ▶ Usage

Optimization studies can be conducted in BayOTA in multiple ways:
1) Command-line: batch mode or single run
2) Python prompt: batch or single run
3) Jupyter notebook: batch or single run

#### 🔀 Run in batch with the slurm manager

First, customize a study .ini file as desired in./bin/studies,\
Then, execute `./bin/shell_scripts/conduct_study.bash`

#### ⌨️ From the command line
To run the standard bash script:

```
# move to the project root
cd bayota/

# run the script (and you can include --daemon argument to detach process and run with no hangup)
./bin/bayota
```

#### 🐍 From the python prompt

    >>> from efficiencysubproblem.src.study import Study

    # Create a model instance
    >>> s = Study(objectivetype='costmin', geoscale='county', geoentities=['Adams, PA'])

    # Solve the instance and get results
    >>> solveroutpath, csvpath, df, objective, feasible = s.go(constraint=5)

#### 📓 From a jupyter notebook
The approach to use in a notebook is the same as the python prompt.\
Some example notebooks are provided in the bin/ directory.

# 🐛 Troubleshooting & debugging

* (NOT YET IMPLEMENTED) Use `--verbose` to output commands that bayota executes.
* (NOT YET IMPLEMENTED) Use `--debug` to output configuration and additional (error) logs.

## 🗣️ Who do I talk to?

* The U.S. EPA Chesapeake Bay Program
* Daniel E. Kaufman: dkaufman@chesapeakebay.net