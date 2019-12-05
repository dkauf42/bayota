#!/usr/bin/env python
""" An example of how we can extract metadata tables given a scenarioId from SQL Server

Example:
    `python ExtractMetadataTables.py <server> <databasename> <source dir> <userpwdfile>`
    `python ExtractMetadataTables.py SQL2T ScenarioBuilderV3Source ../../data/test_source userpwdfile`
    `./castjeeves/sqltables/ExtractMetadataTables.py SQL2T ScenarioBuilderV3Metadata ~/bayota_ws_0.1b2/data ~/.sql/cast_id 5388`

"""
import csv
import sys
import time
import pyodbc
import pandas as pd
from castjeeves.sqltables import Metadata

if len(sys.argv) < 5:
    raise ValueError("We need server, database name, output directory, and a user/password file!")

# else, let's extract
server = sys.argv[1]  # 'SQL2D' or 'localhost'
database = sys.argv[2]  # 'ScenarioBuilderV3Metadata'
METADATA_PATH = sys.argv[3]  # data/test_metadata
userpwdfile = sys.argv[4]

scenarioid = None
if len(sys.argv) > 5:
    scenarioid = sys.argv[5:]  #

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

metadata = Metadata()
for tblName in metadata.getTblList():
    print("extracting table:", tblName)
    
    if (tblName == 'ImpBmpSubmittedLand') or (tblName == 'InvalidBmpSubmittedLand'):
        if not scenarioid:
            print(f"scenarioid not defined. skipping {tblName} table.")
            continue
        query = f"SELECT * FROM dbo.{tblName} WHERE ScenarioId in ({', '.join(scenarioid)})"
    else:
        query = f"SELECT * from dbo.{tblName}"
    print(f"  using query=={query}")
    
    output_file = METADATA_PATH+"/"+tblName+".csv"

    cursor = cnxn.cursor()
    cursor.execute(query)
    blocksize = 500000
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow([x[0] for x in cursor.description])  # column headers

        i = 0
        while True:
            i += 1
            results = cursor.fetchmany(blocksize)
            print(f"Block {i} - fetching ", blocksize, " rows")
            if not results:
                break
            for row in results:
                writer.writerow(row)

    time.sleep(0.1)
