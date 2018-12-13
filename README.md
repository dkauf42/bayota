# Overview

"BayOTA" (Bay Optimization Tools for Analysis) is a repository of
optimization and analysis tools, designed for use by the partners of the
Chesapeake Bay Program (CBP) as well as the general public as part of the Optimization Tool
Development Project (EPA-R3-CBP-16-03).
Specifically, these tools extend the functionality of -
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
* [Troubleshooting & debugging](#-troubleshooting--debugging)
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
│   └── cli/
│   └── jnotebooks/
│   └── python_scripts/
│   └── run_specs/
│   └── scripts_by_level/
│   └── shapefiles/
│
├── data                   <- source data CSVs, excel files
│
├── castjeeves             <- PACKAGE to access, query, and parse source data from the Chesapeake Bay Assessement Scenario Tool (CAST)
│   ├── __init__.py
│   └── ...
│
├── efficiencysubproblem   <- PACKAGE to solve optimization problem involving 'Efficiency' Best Management Practices (BMPs) of CAST
│   ├── __init__.py
│   └── ...
│
├── sandbox                <- PACKAGE for automated generation of valid BMP input files for use with CAST
│   ├── __init__.py
│   └── ...
│
├── bayota_settings        <- PACKAGE that configures directory paths (output, graphics, & logging). Contains example config files.
│   ├── __init__.py
│   └── ...
│
├── bayota_util            <- PACKAGE for utility methods that haven't yet found a home elsewhere
│   ├── __init__.py
│   └── ...
│
├── setup.py
├── MANIFEST.in
├── Dockerfile_36
├── LICENSE
├── VERSION
```

#### Other paths used by this project

(These paths are set during install by the `bayota_settings` package)

***Note:*** *Three config files will be copied into `~/.config/${USER}/` during the first install (or first test run). \
These files set up local paths and formatting and are central to conducting BayOTA optimization studies.*

- `user_config.ini` specifies output path stems (for stdout, graphics, and logs)
- `bash_config.con` specifies the path of the project directory.
- `logging_config.cfg` specifies the format and targets of log messages.

*These files will not be changed by subsequent code executions after being generated.*\
*Example config files can be found in the `bayota_settings` package.*

# ⚙ How do I get set up?

###### Ensure the IPOPT solver is installed and in $PATH

The Ipopt solver must be compiled/installed separately in order to solve Efficiency BMP optimization problems.
- Instructions can be found at https://www.coin-or.org/Ipopt/documentation/node14.html
- After installation, the Ipopt executable location must be added to the environment $PATH variable


#### 👥 Clone the repository

-- Check out a clone of this repository to a location of your choice, e.g.
```
git clone https://gitlab.com/daka42/bayota.git ~/bayota
```

-- From the project directory, get the latest version:

```
cd bayota/

git pull
```

#### 🏡 Configure before installing

-- Customize the following values in `bayota_settings/install_config.ini`:
- `project_home`
- `repo_top`


#### 💾 Install packages

-- From the project dir (`bayota/`), enter:

```
pip install .
```


#### 🛣️ Double-check the local paths

During the first install (or first test run), default configuration files will be generated.\
In `bayota_ws_${version}/config/`, customize values within:

-- `user_config.ini` to direct output to the desired directories.\
-- `bash_config.con` to specify the project home.


#### ✅ Test the installation

-- From the project directory, run the automated test suites:

```
cd bayota/

python castjeeves/setup.py test

python efficiencysubproblem/setup.py test
```

***Note:*** *Tests can be run from the project directory (`bayota/`) even though they are located within each package.\
If you try to run `python setup.py test` from the project dir directly, you will get an error message like:\
"no tests specified at the top(bayota package)-level".*

***Note:*** *To remove the test files after running the tests, use `python setup.py clean`.*

-- **If the tests pass, you should be good to go!**

# ▶ Usage

Optimization studies can be conducted in BayOTA in multiple ways:
1) Command-line: batch mode or single run
2) Python prompt: batch or single run
3) Jupyter notebook: batch or single run

#### ⌨ From the command line
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

```
python setup.py clean
```

--- To remove development version of package (i.e., remove it from easy-install.pth and delete the .egg-link)

```
python setup.py develop --uninstall
```


--- To uninstall the python packages from your environment (site-packages):

```
pip uninstall bayota
```

--- To remove everything (uninstall the python packages and then delete the source directory):

```
pip uninstall bayota
rm -r bayota/
```

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

Funding Acknowledgment:

* U.S. Federal Grant EPA-R3-CBP-16-03 -
"Chesapeake Bay Program Office Fiscal Year 2016 Request for Proposals for Chesapeake Bay Optimization Tool Development"

## 🎓 License
GNU General Public License

## 🗣️ Who do I talk to?

* The U.S. EPA Chesapeake Bay Program
* Daniel E. Kaufman: dkaufman@chesapeakebay.net