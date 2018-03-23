# This version corresponds to Nov 17 version of CBPO SQL code

## Setup

Before you can start using CBPO Python, please make sure to install the following necessary packages:

* Python 3.4 or up
	* The best package to use is Anaconda 3.5 or up, for example
		- For windows, check [https://repo.continuum.io/archive/Anaconda3-4.2.0-Windows-x86_64.exe](https://repo.continuum.io/archive/Anaconda3-4.2.0-Windows-x86_64.exe)
		- For linux, check [https://repo.continuum.io/archive/Anaconda3-4.2.0-Linux-x86_64.sh](https://repo.continuum.io/archive/Anaconda3-4.2.0-Linux-x86_64.sh)
* Pandas
	* If you installed Anaconda 3.5, then it already comes with pandas
	* Or else you can just install through 'pip':
        - ```python pip install pandas```

* (Optional) pyodbc/sqlalchemy for connecting to sql server
	* Similarly, install with python pip command
        - ```pip install pyodbc sqlalchemy```
    * You only need one of them, but in examples, we use both to demonstrate how they get used

## Project files

* `/src/README.md`: This file, contains instructions on how the project structure and on how to use PyCast model in multiple examples.
* `/src/cbpo_module`: There are three main modules for cbpo python pycast model:
	* `source_data` and `medadata` modules are for handling loading of source and metadata tables

* `/src/test_run.sh`: This script contains all examples of how to use PyCast model in different situations.
* `/src/ExtractSourceTables.py`: An example of how to extract source tables from SQL Server into a local directory.
* `/src/ExtractMetadataTables.py`: An example of how to extract metadata tables from SQL Server into a local directory.


## How to run PyCast

Since PyCast is written using Python 3, it can be run locally or on a cluster (e.g. being distributed using Spark cluster such as EMR on AWS). In this part, we'll demonstrate on how to use `cbpo_module` through several examples. Check `/src/test_run.sh` for actual running code.

* Ideally, PyCast should be run such as all source tables and metadata tables are csv files located on a local drive or on S3, or on Hadoop file system. Each table should have header columns on the first row.
* PyCast can also run while all source tables and metadata tables are located on a SQL Server. However this approach is very inefficient due to the read/write from/to SQL Server.
* PyCast works with pandas dataframes much like how SQL works with tables, so where you store input and output data tables only affect I/O operations, not the model.

### Run PyCast with one scenarioId

#### Option 1: Data tables are located on local drive
You can prepare all source and metadata tables somewhere locally beforehand. Or you can extract them directly from SQL Server (only applicable when you prefer this way, and you'll need SQL server credentials).

**(Optional) Extract source tables (Do this only once for all source tables)**
* Go to `/src` and run:
	- `python ExtractSourceTables.py <server> <databasename> <username> <pass> <source dir>`

**(Optional) Extract metadata tables for one scenarioId value (e.g. 1027)**
* Go to `/src` and run:
    - `python ExtractMetadataTables.py <server> <databasename> <username> <pass> <metadata dir> <scenarioId>`

* Write output to local directory
    - `python test_main_sqlserver_local.py <server> <source_db> <metadata_db> <username> <pass> <OUTPUT_PATH> <scenarioId>`
* Write output to History database
    - `python test_main_sqlserver_sqlserver.py <server> <source_db> <metadata_db> <history_db> <username> <pass> <scenarioId>`

### Run PyCase with many scenarioIds
In this case, we only need to load source tables once into PyCast Scenario and loop over a list of scenarioIds to run the model.
* `python test_main_sqlserver_sqlserver_manyIds.py <server> <source_db> <metadata_db> <history_db> <username> <pass> <scenarioId file>`


## Notes
* An issue with SQL Driver may occur, this needs to be resolved if driver is not there
* From MSSQL side, credentials need to be created to allow access to databases
