##################################
# An example of how we can extract metadata tables given a scenarioId from SQL Server
# using python
import sys
import pyodbc
import pandas as pd

from cbpo_module.metadata import Metadata

##################################
# if len(sys.argv)<7:
#     print("We need server, database name, username, password, output directory, and scenarioId value!")
#     sys.exit()
#
# #else, let's extract
# server = sys.argv[1] #'localhost'
# database = sys.argv[2] #'ScenarioBuilderV3Metadata'
# username = sys.argv[3] #'test'
# password = sys.argv[4] #'test'
# METADATA_PATH =sys.argv[5] #test
# scenarioId =sys.argv[6] #2272
# #################################
#
# cnxn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server}'
#                       ';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

# NEW CODE BY DEKAUFMAN FOR LOCAL CONNECTION USING WINDOWS AUTHENTICATION
if len(sys.argv) < 5:
    print("We need server, database name, username, password, output directory, and scenarioId value!")
    sys.exit()

# else, let's extract
server = sys.argv[1]  # 'localhost'
database = sys.argv[2]  # 'ScenarioBuilderV3Metadata'
METADATA_PATH = sys.argv[3]  # test
scenarioId = sys.argv[4]  # 2272
#################################

cnxn = pyodbc.connect('DRIVER={SQL Server Native Client 11.0}' +
                      ';SERVER=' + server +
                      ';DATABASE=' + database +
                      ';Trusted_Connection=yes')

metadata = Metadata()
for tblName in metadata.getTblList():
    print("extracting table:", tblName)
    query = "SELECT * from dbo."+tblName+" where ScenarioId="+scenarioId
    if tblName == "TblPointSourceDataSets":
        query = "SELECT * from dbo."+tblName
    df = pd.read_sql(query, cnxn)
    df = df.rename(columns={column: column.lower() for column in df.columns})
    
    output_file = METADATA_PATH+"/"+tblName+".csv"
    df.to_csv(output_file, sep=',', encoding='utf-8', index=False)
