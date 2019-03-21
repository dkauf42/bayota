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

* Scripts (shell scripts, jupyter notebooks, python scripts)
* Config files that specify optimization study parameters

#### Directory Tree
```
bin
│
├── README.md              <- README describing how to conduct optimization studies
│
├── jnotebooks             <- Jupyter notebooks.
│   └── ...                   Naming convention is a number (for ordering), the creator's initials,
│                             and a short `_` delimited description, e.g. `1.0-jqp-initial_data_exploration`.
│
├── python_scripts         <- python scripts for easy access to optimization studies and results analyses.
│   └── ...
│
├── run_scripts            <- scripts for batch optimization studies.
│   └── ...
│
├── specification_files    <- .yaml files that allow detailed specification of study parameters
│   └── ...
│
```


# ▶ Usage

Optimization studies can be conducted in BayOTA in multiple ways:
1) Command-line: batch mode or single run
2) Python prompt: batch or single run
3) Jupyter notebook: batch or single run

#### ⌨️ Command Line Interface

Several alternative CLI scripts are available with varying degrees of completeness:

###### 1) a python cli: "conductor_cli.py"

--- Two commands are available for conductor_cli.py:

* ```createinstance -f [CONFIG_FILE]``` - instantiate a model using options specified in FILE
* ```solveinstance -i [INSTANCE_FILE]``` - solve a model instance with specified constraint

--- Some examples, executed from the project root (`cd bayota/`):
- Bundle with main color changed to orange:\
`$ ./bin/conductor_cli.py createinstance -f bin/studies/study_costmin_county_annearundelmd.ini
- Serve with nativeScrollbars option set to true:\
`$ ./bin/conductor_cli.py createinstance [spec] --options.nativeScrollbars`
- Bundle using custom template (check default template for reference):\
`$ ./bin/conductor_cli.py solveinstance -i saved_instance.pickle`

--- For more details run:\
`conductor_cli.py --help`, or\
`conductor_cli.py <command> --help`

###### 2) a standard bash script

--- To run the script (from the project root (`cd bayota/`):\
`> ./bin/conduct_study_on_login_node.bash`

(and you can include --daemon argument to detach process and run with no hangup)

#### 🔀 Run studies in parallel, using slurm

First, customize a study .ini file as desired in./bin/studies,\
Then, execute `./bin/shell_scripts/conduct_study.bash`

#### 🐍 From the python prompt

    >>> from efficiencysubproblem.src.study import Study

    # Create a model instance
    >>> s = Study(objectivetype='costmin', geoscale='county', geoentities=['Adams, PA'])

    # Solve the instance and get results
    >>> solveroutpath, csvpath, df, objective, feasible = s.go(constraint=5)

#### 📓 From a jupyter notebook
The approach to use in a notebook is the same as the python prompt.\
Some example notebooks are provided in the bin/ directory.

They try to follow the guidance of http://pbpython.com/notebook-process.html:

- "A good name for the notebook (as described above)
- A summary header that describes the project
- Free form description of the business reason for this notebook. I like to include names, dates and snippets of emails to make sure I remember the context.
- A list of peoscple/systems where the data originated.
- I include a simple change log. I find it helpful to record when I started and any major changes along the way. I do not update it with every single change but having some date history is very beneficial."

# 🐛 Troubleshooting & debugging

* (NOT YET IMPLEMENTED) Use `--verbose` to output commands that bayota executes.
* (NOT YET IMPLEMENTED) Use `--debug` to output configuration and additional (error) logs.

## 🗣️ Who do I talk to?

* The U.S. EPA Chesapeake Bay Program
* Daniel E. Kaufman: dkaufman@chesapeakebay.net