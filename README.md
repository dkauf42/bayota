# BayOTA

BayOTA (Bay Optimization Tools for Analysis) is designed for use by the partners of the
Chesapeake Bay Program (CBP) as well as the general public as part of the Optimization Tool
Development Project (EPA-R3-CBP-16-03).
Specifically, this extends the functionality of -
and helps users of - CAST (the Chesapeake Bay Assessement Scenario Tool),
which is the CBP Phase 6 time-averaged watershed model.

<strong>Table of Contents</strong>

* [How do I get set up?](#-how-do-i-get-set-up)
    1. [Ensure the IPOPT solver is installed and in $PATH](#1-ensure-the-ipopt-solver-is-installed-and-in-path)
    2. [Clone the repository](#2-clone-the-repository)
    3. [Configure the workspace before installing](#3-configure-the-workspace-before-installing)
    4. [Install packages](#4-install-packages)
    5. [Double-check the local paths](#5-double-check-the-local-paths)
    6. [Test the installation](#6-test-the-installation)
* [Usage](#-usage)
    - [Specification Files](#specification-files)
    - [Batch Sequence](#batch-sequence)
    - [Running from the command line](#1-running-from-the-command-line)
    - [Running from the python prompt](#2-running-from-the-python-prompt)
    - [Running from a jupyter notebook](#3-running-from-a-jupyter-notebook)
    - [Cleaning up after installation and runs](#-cleaning-up-after-intallation-and-runs)
    - [Debugging or troubleshooting](#-debugging-or-troubleshooting)
* [Project structure](#-project-structure)
    - [Components](#components)
    - [Directory Tree](#directory-tree)
* [Updating](#-updating)
* [Uninstalling](#-uninstalling)
* [Other Notes](#-other-notes)
* [Credits](#-credits)
* [Disclaimer](#-disclaimer)
* [License](#-license)
* [Who do I talk to?](#-who-do-i-talk-to)

# ⚙ How do I get set up?

***Note: The CAST Source data is not included in this repository. \
Full installation and usage is not possible without the source data.***

##### 1📉 Ensure the IPOPT solver is installed and in $PATH

-- The Ipopt solver must be installed separately in order to solve Efficiency BMP optimization problems.
- Option 1: compile/install using instructions found at https://www.coin-or.org/Ipopt/documentation/node14.html
- Option 2: install using conda: `conda install ipopt`

-- After installation, the Ipopt executable location must be added to the environment $PATH variable


##### 2👥 Clone the repository

-- Check out a clone of this repository to a location of your choice, e.g.
```
git clone https://gitlab.com/daka42/bayota.git ~/bayota
```

-- From the project directory, get the latest version:

```
cd bayota/

git pull
```

-- Most work will be done in the 'develop' branch, so switch to it with git checkout

```
git checkout develop
```

##### 3🏡 Configure the workspace before installing

Set up where you would like to have a bayota 'workspace'.  \
Specify this before installing, by doing one of the following...

- Set the following ENV variables:
    - `BAYOTA_HOME` (should point to the directory where the bayota repo is located), and 
    - `BAYOTA_WORKSPACE_HOME` (should point to the directory where workspace will be located)
  
OR
- Customize the following values in `bayota_settings/install_config.ini`:
    - `repo` (should point to the directory where the bayota repo is located)
    - `local_workspace_stem`

***Note:*** *Important filepaths are set (during install) by the `bayota_settings` package.\
These paths include general output, logging, temporary files, etc., and are defined in the following three config files:*

- `bash_config.con` *specifies the path of the project directory.*
- `logging_config.yaml` *specifies the format and targets of log messages.*
- `user_config.ini` *specifies output path stems (for stdout, graphics, and logs)*

*These three config files are required for conducting BayOTA optimization studies, and will be copied into `~/bayota_ws_{version}/config/` during the first install (or first test run).*

*These files will not be programmatically changed by subsequent code executions after being generated.*\
*The example/default config files can be found in the `bayota_settings` package.*


##### 4💾 Install packages

-- From the project dir (`bayota/`), enter:

```
pip install .
```


##### 5🛣️ Double check the local paths

During the first install (or first test run), default configuration files are generated.\
-- In `bayota_ws_{version}/config/`, customize values within:

- `user_config.ini` to direct output to the desired directories.\
- `bash_config.con` to specify the project home.


##### 6✅ Test the installation

-- From the project directory, run the automated test suites:

```
python setup.py test
```

Or, if you want to run it from the installed package:
```
pytest --pyargs bayota
```

Or, for one package at a time:
```
pytest --pyargs bayota.castjeeves
pytest --pyargs bayota.bayom_e
```

***Note:*** *To remove the test files after running the tests, use `python setup.py clean`.*

-- **If the tests pass, you should be good to go!**

# ▶ Usage

Optimization studies can be conducted in BayOTA in multiple ways:
1) Command-line: batch mode or single run
2) Python prompt: batch or single run
3) Jupyter notebook: batch or single run

#### Specification Files
Typical usage requires setting up model and run configurations in 'specification files'. 
These are defined (by default) in a workspace subdirectory, and there are 3 types:
* **batch specs** - These set up one or more studies, by specifying:
    - geographies
    - names of model and experiment spec files to use
    - other options, such as moving/translating solution files after solving
* **model specs** - These set up the model objectives/constraints
* **experiment specs** - These allow modification of the model for particular experiments and running through different values of constraints.

#### Batch Sequence

<img src="./.images/code_organization_specification_files_colored_like_graph_simple.png" alt="batch_sequence" width="295" height="377"/>

#### 1⌨ Running from the command line
-- First, change directory to the project root (`cd bayota/`).

Two methods of running are provided. \
They each provide the ability to run a batch of optimization studies automatically. The options are to use either the 
Slurm job manager or AWS Batch in docker containers.  To execute, one would run either:
`bin/run_scripts/docker_batch_runner.py`
or
`bin/run_scripts/slurm_batch_runner.py`

Note: When either of these are run, they will automatically call the following run_steps during execution:
1) `bin/run_steps/step1_generatemodel.py`
2) `bin/run_steps/step2_modifymodel.py`
3) `bin/run_steps/step3_solveonetrial.py`

###### Batch runs are set up using 'specification files'. These will be in one's workspace.

-- Example command for a batch of studies:
* `-d` (or `--dryrun`) argument can be included to only print the commands that would be submitted without running them
* `--no_slurm` argument needed when not using the SLURM job manager
* `--help` for command syntax

```
./bin/run_scripts/run_step0_batch_of_studies.py -n calvertMD_cost_and_load_objective_experiments.yaml --dryrun
```


#### 2🐍 Running from the python prompt
```python
from bayom_e.model_handling.interface import build_model
from bayom_e.solver_handling import solvehandler

# Create a model instance
model_spec_name = 'costmin_total_Npercentreduction'
model, dataplate = build_model(model_spec_name=model_spec_name,geoscale='county',geoentities='Perry, PA',baseloadingfilename='2010NoActionLoads_updated.csv',savedata2file=False,log_level='INFO')

# Set a constraint level
model.percent_reduction_minimum['N'] = 20

# Solve the instance and get results

solvername = 'ipopt'
instance, results, feasible = solvehandler.solve(localsolver=True, solvername=solvername,
                                                 instance=model)
```

#### 3📓 Running from a jupyter notebook
The approach to use in a notebook is the same as the python prompt.

#### 🧹 Cleaning up after intallation and runs

--- To remove build files created by "`python setup.py install`" or to remove temporary files created in the project home during a run:

```
python setup.py clean
```

#### 🐛 Debugging or troubleshooting

* Add `--log_level=DEBUG` argument when running from the command line to output the most verbose logging messages.

# 📁 Project Structure

#### Components

<img src="./.images/components_20200325.png" alt="components" width="489" height="311"/>

#### Directory Tree
```
bayota
│
├── README.md              <- Top-level README for users/developers of this project.
├── CHANGELOG.md           <- Documentation of notable changes to this project
│
├── bin                    <- scripts for running from the command-line and performing analyses
│   ├── aws_scripts/
│   ├── run_scripts/
│   ├── run_steps/
│   ├── python_scripts/
│   └── my_test_scripts/
│
├── bayom_e                <- *Python package* to solve optimization problem involving 'Efficiency' Best Management Practices (BMPs) of CAST
│   ├── config.py
│   ├── data_handling/
│   ├── model_handling/
│   ├── solver_handling/
│   ├── solution_handling/
│   └── ...
|
├── castjeeves             <- *Python package* to access, query, and parse source data from the Chesapeake Bay Assessement Scenario Tool (CAST)
│   ├── jeeves.py
│   ├── sourcehooks/
│   ├── sqltables/
│   └── ...
│
├── bayota_settings        <- *Python package* that configures directory paths (output, graphics, & logging). Contains example config files.
│   ├── base.py
│   ├── log_setup.py
│   └── ...
│
├── bayota_util            <- *Python package* for utility methods that haven't yet found a home elsewhere
│   ├── s3_operations.py
│   ├── spec_and_control_handler.py
│   ├── str_manip.py
│   └── ...
│
├── Dockerfile
├── LICENSE
├── MANIFEST.in
├── setup.py
├── VERSION
```

# 🚮 Updating

--- To use the latest version of this repository:
- Enter the `bayota/` directory
- Activate your desired environment
- Run the commands:

   ```
   git pull
   git checkout master
   pip install . --upgrade
   ```

# 🚮 Uninstalling

--- To uninstall the python packages from your environment (site-packages):

```
pip uninstall bayota
```

--- *(less common) To remove development version of package (i.e., remove it from easy-install.pth and delete the .egg-link)*

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


## 💕 Credits

Major dependencies:

* [Pyomo](https://www.pyomo.org/)
* [IPOPT solver](https://projects.coin-or.org/Ipopt)
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

## 📧 Who do I talk to?

* The U.S. EPA Chesapeake Bay Program
* Daniel E. Kaufman: dkaufman@chesapeakebay.net