# BayOTA

BayOTA (Bay Optimization Tool for Analyses) is designed for use by the partners of the
Chesapeake Bay Program (CBP) as well as the general public as part of the Optimization Tool
Development Project (EPA-R3-CBP-16-03).
Specifically, this extends the functionality of -
and helps users of - CAST (the Chesapeake Bay Assessement Scenario Tool),
which is the CBP Phase 6 time-averaged watershed model.

<br>

This README documents steps necessary to get the application up and running.

<details>
<strong>Table of Contents</strong>

* [How do I get set up?](#-how-do-i-get-set-up)
* [Usage](#-usage)
* [How do I uninstall?](#-how-do-i-uninstall)
* [Troubleshooting & debugging](#-troubleshooting--debugging)
* [Project structure](#project_structure)
* [Credits](#-credits)
* [License](#-license)
* [Who do I talk to?](#-who-do-i-talk-to)
</details>

# ⚙ How do I get set up?

#### 1. Ensure the IPOPT solver is installed and in $PATH

The Ipopt solver must be compiled/installed separately in order to solve Efficiency BMP optimization problems.
- Instructions can be found at https://www.coin-or.org/Ipopt/documentation/node14.html
- After installation, the Ipopt executable location must be added to the environment $PATH variable


#### 2. 👥 Clone the repository

-- Check out a clone of this repository to a location of your choice, e.g.
```
git clone https://gitlab.com/daka42/bayota.git ~/bayota
```

-- From the project directory, get the latest version:

```
cd bayota/

git pull
```

#### 3. 🏡 Configure before installing

-- Customize the following values in `bayota_settings/install_config.ini`:
- `project_home`
- `repo_top`


#### 4. 💾 Install packages

-- From the project dir (`bayota/`), enter:

```
pip install .
```


#### 🛣️ Double-check the local paths

During the first install (or first test run), default configuration files will be generated.\
In `bayota_ws_{version}/config/`, customize values within:

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

Five 'run' scripts are provided.  They provide the ability to run a batch of optimization studies automatically, \
or with individual steps run separately. They are, in order of their automated execution during a batch submission:
1) `run_step0_batch_of_studies.py`
2) `run_step1_single_study.py`
3) `run_step2_generatemodel.py`
4) `run_step3_conductexperiment.py`
5) `run_step4_solveonetrial.py`

###### Batch runs are set up using 'specification files'. These can be found in `bin/specification_files`.

#### ⌨ From the command line
First, change directory to the project root (`cd bayota/`).

Then, execute one of the following commands.
* -d (or --dryrun) argument can be included to only print the commands that would be submitted without running them
* -h brings up command help


***Batch of studies***
```
./bin/run_scripts/run_step0_batch_of_studies.py -f ./bin/run_specs/batch_study_specs/calvertMD_cost_and_load_objective_experiments.yaml --dryrun
```
***A single study***
```
./bin/run_scripts/run_step1_single_study.py -g CalvertMD -n calvertMD_cost_experiments --dryrun
```
***Generate a study model***
```
./bin/run_scripts/run_step2_generatemodel.py -g CalvertMD -n costmin_total_percentreduction -sf ~/bayota_ws_0.0.1/temp/model_instances/modelinstance_costmin_total_percentreduction_CalvertMD.pickle --dryrun
```
***Conduct an experiment***
```
./bin/run_scripts/run_step3_conductexperiment.py -n ./bin/run_specs/experiment_specs/costmin_1-40percentreduction -sf /Users/Danny/bayota_ws_0.0.1/temp/model_instances/modelinstance_costmin_total_percentreduction_CalvertMD.pickle --dryrun
```
***Solve a single trial***
```
./bin/run_scripts/run_step_4_solveonetrial.py -sf ~/bayota_ws_0.0.1/temp/model_instances/modelinstance_costmin_total_percentreduction_CalvertMD.pickle -tn experiment--costmin_1-40percentreduction--_modifiedvar--percent_reduction_minimum--_trial0040 --solutions_folder_name costmin_1-40percentreduction -m '{"variable": "percent_reduction_minimum", "value": 40, "indexer": "N"}' --dryrun
```


#### 🐍 From the python prompt

    >>> from efficiencysubproblem.src.study import Study

    # Create a model instance
    >>> s = Study(objectivetype='costmin', geoscale='county', geoentities=['Adams, PA'])

    # Solve the instance and get results
    >>> solveroutpath, csvpath, df, objective, feasible = s.go(constraint=5)

#### 📓 From a jupyter notebook
The approach to use in a notebook is the same as the python prompt.\
Some example notebooks are provided in the bin/jnotebooks/ directory.

# 🚮️ How do I uninstall?

--- To remove build files created by "`python setup.py install`":

```
python setup.py clean
```


--- To uninstall the python packages from your environment (site-packages):

```
pip uninstall bayota
```

--- To remove development version of package (i.e., remove it from easy-install.pth and delete the .egg-link)

```
python setup.py develop --uninstall
```

--- To remove everything (uninstall the python packages and then delete the source directory):

```
pip uninstall bayota
rm -r bayota/
```

# 📔 Other Notes

To use pynumero package from Pyomo:
- `scipy` is required
- may need to run `conda install -c conda-forge pynumero_libraries` for ASL library


# 🐛 Troubleshooting & debugging

* Use `--log_level=DEBUG` to output the most verbose logging messages.

<a id='project_structure'></a>
# 📁 Project Structure

#### Directory Tree
```
bayota
│
├── README.md              <- Top-level README for users/developers of this project.
├── CHANGELOG.md           <- Documentation of notable changes to this project
│
├── bin                    <- scripts (python, bash, slurm, jupyter notebooks) for running from the command-line and performing analyses
│   └── jnotebooks/
│   └── python_scripts/
│   └── run_scripts/
│   └── specification_files/
│
├── data                   <- source data CSVs, excel files
│
├── castjeeves             <- Python *PACKAGE* to access, query, and parse source data from the Chesapeake Bay Assessement Scenario Tool (CAST)
│   ├── __init__.py
│   └── ...
│
├── efficiencysubproblem   <- Python *PACKAGE* to solve optimization problem involving 'Efficiency' Best Management Practices (BMPs) of CAST
│   ├── __init__.py
│   └── ...
│
├── sandbox                <- Python *PACKAGE* for automated generation of valid BMP input files for use with CAST
│   ├── __init__.py
│   └── ...
│
├── bayota_settings        <- Python *PACKAGE* that configures directory paths (output, graphics, & logging). Contains example config files.
│   ├── __init__.py
│   └── ...
│
├── bayota_util            <- Python *PACKAGE* for utility methods that haven't yet found a home elsewhere
│   ├── __init__.py
│   └── ...
│
├── Dockerfile_37_multistage
├── LICENSE
├── MANIFEST.in
├── setup.py
├── VERSION
```

#### Other file paths used by this project

Important filepaths are set (during install) by the `bayota_settings` package.\
These paths include general output, logging, temporary files, etc.\
Such filepaths are defined in the following three config files.

***Note:*** *These three config files will be copied into `~/bayota_ws_{version}/config/` during the first install (or first test run). \
These files define local paths (and log formatting) and are required for conducting BayOTA optimization studies.*

- `bash_config.con` specifies the path of the project directory.
- `logging_config.yaml` specifies the format and targets of log messages.
- `user_config.ini` specifies output path stems (for stdout, graphics, and logs)

*These files will not be changed by subsequent code executions after being generated.*\
*Example config files can be found in the `bayota_settings` package.*

## 💕 Credits

Major dependencies:

* [Pyomo](https://www.pyomo.org/)
* [IPOPT solver](https://projects.coin-or.org/Ipopt)
* [AMPLPY](https://github.com/ampl/amplpy)
* [Pandas](https://pandas.pydata.org/)
* [NumPy](https://www.numpy.org/)

Funding Acknowledgment:

* U.S. EPA cooperative agreement under federal grant EPA-R3-CBP-16-03 - "Chesapeake Bay Optimization Tool Development"

## ❗ Disclaimer

This is a beta version of the Bay Optimization Tools for Analysis (BayOTA), in the process of being tested. It is provided on an “as is” and “as available” basis and is believed to contain defects. A primary purpose of this beta testing release is to solicit feedback on performance and defects. The Chesapeake Bay Program Office (CBPO) does not give any express or implied warranties of any kind, including warranties of suitability or usability of the website, its software, or any of its content, or warranties of fitness for any particular purpose.
All users of BayOTA are advised to safeguard important data, to use caution, and not to rely in any way on correct functioning or performance of the beta release and/or accompanying materials. CBPO will not be liable for any loss (including direct, indirect, special, or consequential losses) suffered by any party as a result of the use of or inability to use BayOTA, its software, or its content, even if CBPO has been advised of the possibility of such loss.
Should you encounter any bugs, glitches, lack of functionality, or other problems on the website, please let us know. We can be reached at e-mail address dkaufman@chesapeakebay.net. Your help in this regard is greatly appreciated!

## 🎓 License
The 3-Clause BSD License

## 🗣️ Who do I talk to?

* The U.S. EPA Chesapeake Bay Program
* Daniel E. Kaufman: dkaufman@chesapeakebay.net