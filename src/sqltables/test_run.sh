# This script contains examples of how to run pycast model 
# We'll use 1027 as an sample scenarioId
#Check cbpo_python/README.md for more information

#Examples
server='localhost' #location of SQL Server 
source_db='ScenarioBuilderV3Source' 
metadata_db='ScenarioBuilderV3Metadata'
history_db='ScenarioBuilderV3History'
username='test' #SQL Server username
password='test' #SQL Server password
scenarioId='1027' #sample scenarioId

source_dir='source_dir' #sample directory to store extracted source tables
metadata_dir='metadata_dir' #sample directory to store extracted metadata tables
output_dir='output_dir' #sample output directory


# Example 1. Extract source tables
mkdir ${source_dir}
python ExtractSourceTables.py $server ${source_db} $username $password ${source_dir}

# Example 2. Extract metadata tables for 1027
mkdir ${metadata_dir}
python ExtractMetadataTables.py $server ${metadata_db} $username $password ${metadata_dir} $scenarioId

# NOTE:
#You can also run PyCast without extracting tables into csv files, Skip 1,2,3 above
#However this will be slow since it reads directly from SQL Server
