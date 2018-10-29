# Overview

"BayOTA" (Bay Optimization Tools for Analysis) is a repository of
optimization and analysis tools created to serve the
Chesapeake Bay Program (CBP) Partners, as part of the Optimization Tool
Development Project (EPA-R3-CBP-16-03).
Specifically, these tools are designed to add functionality to -
and help users of - CAST (the Chesapeake Bay Assessement Scenario Tool),
which is the CBP Phase 6 time-averaged watershed model.

* Version 0.0.1

This README documents steps necessary to get the application up and running.

<details>
 <summary><strong>Table of Contents</strong> (click to expand)</summary>

* [Project structure](#-project-structure)
* [How do I get set up?](#-how-do-i-get-set-up)
* [Usage](#-usage)
* [How do I uninstall?](#-how-do-i-uninstall)
* [Troubleshooting & debugging](#-troubleshooting-debugging)
* [Credits](#-credits)
* [License](#-license)
* [Who do I talk to?](#-who-do-i-talk-to)
</details>

# 📁 Project Structure

#### Directory Tree
```
bayota
│
├── README.md              <- Top-level README for users/developers of this project.
├── CHANGELOG.md           <- Documentation of notable changes to this project
│
├── bin                    <- scripts (python, bash, slurm, jupyter notebooks) for running from the command-line and performing analyses
│   └── config
│       └── ...
│   └── jnotebooks
│       └── ...
│   └── shell_scripts
│       └── ...
│   └── studies
│       └── ...
│
├── CASTJEEVES             <- PACKAGE to access, query, and parse source data from the Chesapeake Bay Assessement Scenario Tool (CAST)
│   ├── __init__.py
│   └── ...
│
├── EFFICIENCYSUBPROBLEM   <- PACKAGE to solve optimization problem involving 'Efficiency' Best Management Practices (BMPs) of CAST
│   ├── __init__.py
│   └── ...
│
├── SANDBOX                <- PACKAGE for automated generation of valid BMP input files for use with CAST
│   ├── __init__.py
│   └── ...
│
├── BAYOTA_SETTINGS        <- PACKAGE that configures data output, graphics, and logging directory paths
│   └── ...
│
├── BAYOTA_UTIL            <- PACKAGE for utility methods that haven't yet found a home elsewhere
│   ├── __init__.py
│   └── ...
│
├── setup.py
├── MANIFEST.in
├── Dockerfile_36
├── LICENSE
├── default_bash_config.con
├── default_config.ini
├── default_logging_config.cfg
```

#### Other paths used by this project

 - `~/.config/${USER}/` # holds configuration files
 - `~/bayota_output/`  #

(These paths are set during install by the `bayota_settings` package)

# ⚙ How do I get set up?


From the project directory, get the latest version:

```cd bayota/```

```git pull```

#### Local configuration files
During the first install or test run, three default config files will be copied into ```~/.config/${USER}/```\
(These files will not be changed by subsequent project executions.)

Values in these config files should be customized by the user:

- ```bayota_user_config.ini``` specifies output paths.
- ```bayota_bash_config.con``` specifies the project directory.
- ```bayota_logging_config``` specifies the format and targets of log messages.

The configuration files are central to the running of BayOTA packages and set up the local environment\
for conducting optimization studies.

They include the file path of the project directory, the output path stems (for stdout, graphics, and logs),\
and many other settings. Several example configuration files can be found in the project source directory.

#### ✅ Run tests to check whether things work

Tests are located within each package, but should be run from the project dir:

```cd bayota/```

```python efficiencysubproblem/setup.py test```

```python castjeeves/setup.py test```

***Note:*** Tests aren't located at the project level.\
So, if you try to run
```python setup.py test``` from the `bayota/` dir, you will get an error message like:\
"no tests specified at the top(bayota package)-level"

***Note:*** To remove the test files after testing, run ```python setup.py clean```


#### 💾 Install packages

From the project dir (`bayota/`), run:

```python setup.py install```

# ▶ Usage

Optimization studies can be conducted in multiple ways:
1) Command-line: batch mode or single run
2) Python prompt: batch or single run
3) Jupyter notebook: batch or single run

#### ⌨️ From the command line
To run the standard bash script:

```
cd bin/

# set execute permission
chmod +x bayota
chmod +x bayota_efficiency.py

# back up to the project root (bayota/)
cd ..

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

# 🚮️ How do I uninstall?

--- To remove build files created by "`python setup.py install`":

```python setup.py clean```

--- To remove installed package files from your environment (site-packages):

```python setup.py develop --uninstall```

--- To remove everything

```python setup.py develop --uninstall```

```rm -r bayota```

# 🐛 Troubleshooting & debugging

* (NOT YET IMPLEMENTED) Use `--verbose` to output commands that bayota executes.
* (NOT YET IMPLEMENTED) Use `--debug` to output configuration and additional (error) logs.

## 💕 Credits

Major dependencies:

* [Pyomo](https://www.pyomo.org/)
* [IPOPT solver](https://projects.coin-or.org/Ipopt)
* [AMPLPY](https://github.com/ampl/amplpy)
* [Pandas](https://pandas.pydata.org/)
* [NumPy](https://www.numpy.org/)

## 🎓 License
GNU General Public License

## 🗣️ Who do I talk to?

* The U.S. EPA Chesapeake Bay Program
* Daniel E. Kaufman: dkaufman@chesapeakebay.net