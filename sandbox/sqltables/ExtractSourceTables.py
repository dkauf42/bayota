############################################################
# An example of how we can extract source tables from SQL Server
# using python
import sys
import pyodbc
import pandas as pd
import time


# ##################################
# if len(sys.argv)<6:
#     print("We need server, database name, username, password, and source directory!")
#     sys.exit()
#
# #else, let's extract
# server = sys.argv[1] #'localhost'
# database = sys.argv[2] #'ScenarioBuilderV3Source'
# username = sys.argv[3] #'test'
# password = sys.argv[4] #'test'
# SOURCE_PATH =sys.argv[5]
#
# ##################################
#
# cnxn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

# NEW CODE BY DEKAUFMAN FOR LOCAL CONNECTION USING WINDOWS AUTHENTICATION
if len(sys.argv) < 4:
    print("We need server, database name, username, password, output directory, and scenarioId value!")
    sys.exit()

# else, let's extract
server = sys.argv[1]  # 'localhost'
database = sys.argv[2]  # 'ScenarioBuilderV3Source'
SOURCE_PATH = sys.argv[3]
#################################

cnxn = pyodbc.connect('DRIVER={SQL Server Native Client 11.0}' +
                      ';SERVER=' + server +
                      ';DATABASE=' + database +
                      ';Trusted_Connection=yes')

from cbpo_module.source_data import SourceData
sourcedata = SourceData()
for tblName in sourcedata.getTblList():
    if (tblName == 'TblPointSourceData') | (tblName == 'TblLandUsePreBmp'):  # to skip the largest files
        pass
    else:
        print("extracting table:", tblName)

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
