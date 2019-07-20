""" An example of how we can extract source tables from SQL Server using python

Example:
    `python ExtractSourceTables.py <server> <databasename> <source dir> <userpwdfile>`
    `python ExtractSourceTables.py SQL2T ScenarioBuilderV3Source ../../data/test_source userpwdfile

"""
import sys
import pyodbc
import pandas as pd
import time
from castjeeves.sqltables import SourceData

if len(sys.argv) < 5:
    raise ValueError("We need server, database name, output directory path, and a user/password file!")

# else, let's extract
server = sys.argv[1]  # 'SQL2D' or 'localhost'
database = sys.argv[2]  # 'ScenarioBuilderV3Source'
SOURCE_PATH = sys.argv[3]
userpwdfile = sys.argv[4]

# read in the userid and password from the given file
kvars = {}
with open(userpwdfile) as f:
    for line in f:
        if line[0] != '#':
            name, var = line.rstrip('\n').partition("=")[::2]
            kvars[name.strip()] = var
userid = kvars['uid']
password = kvars['pwd']

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}' +
                      ';SERVER=' + server +
                      ';DATABASE=' + database +
                      ';uid=' + userid +
                      ';pwd=' + password)

sourcedata = SourceData()
skipLargest = False  # to skip the largest (>120 MB) files
for tblName in sourcedata.getTblList():
    print("extracting table:", tblName)
    if skipLargest is True:
        if (tblName == 'TblPointSourceData') | (tblName == 'TblLandUsePreBmp'):
            print('...nevermind, we are skipping this table because <skipLargest==True>')
            continue

    query = "SELECT * from dbo."+tblName

    # To read tables all at once
    # df = pd.read_sql(query, cnxn)

    # To read in chunks
    df = pd.DataFrame()
    for chunks in pd.read_sql(query, con=cnxn, chunksize=500000):
        df = df.append(chunks)

    df = df.rename(columns={column: column.lower() for column in df.columns})
    if tblName == "TblBmpGroup":
        df["ruleset"] = df["ruleset"].astype(str).str.lower()

    output_file = SOURCE_PATH+"/"+tblName+".csv"
    df.to_csv(output_file, sep=',', encoding='utf-8', index=False)
    time.sleep(0.1)
