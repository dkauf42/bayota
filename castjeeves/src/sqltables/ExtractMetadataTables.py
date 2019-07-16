""" An example of how we can extract metadata tables given a scenarioId from SQL Server

Example:
    `python ExtractMetadataTables.py <server> <databasename> <source dir> <userpwdfile>`
    `python ExtractMetadataTables.py SQL2T ScenarioBuilderV3Source ../../data/test_source userpwdfile

"""
import sys
import time
import pyodbc
import pandas as pd
from castjeeves.src.sqltables.metadata import Metadata

if len(sys.argv) < 5:
    raise ValueError("We need server, database name, output directory, and a user/password file!")

# else, let's extract
server = sys.argv[1]  # 'SQL2D' or 'localhost'
database = sys.argv[2]  # 'ScenarioBuilderV3Metadata'
METADATA_PATH = sys.argv[3]  # data/test_metadata
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

metadata = Metadata()
for tblName in metadata.getTblList():
    print("extracting table:", tblName)
    query = "SELECT * from dbo."+tblName
    #df = pd.read_sql(query, cnxn)

    # To read in chunks
    df = pd.DataFrame()
    for chunks in pd.read_sql(query, con=cnxn, chunksize=500000):
        df = df.append(chunks)

    df = df.rename(columns={column: column.lower() for column in df.columns})
    
    output_file = METADATA_PATH+"/"+tblName+".csv"
    df.to_csv(output_file, sep=',', encoding='utf-8', index=False)
    time.sleep(0.1)
