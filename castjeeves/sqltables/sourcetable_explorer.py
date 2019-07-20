""" For each table in Source, print out a summary (column headers and number of rows) """
import os
import sys
import pandas as pd

from bayota_settings.base import get_source_csvs_dir, get_metadata_csvs_dir

# Input argument is parsed.
if len(sys.argv) < 2:
    raise ValueError("Usage requires table type: 'source' or 'metadata'!")
tabletype = sys.argv[1]

if tabletype.lower() == 'source':
    directory = get_source_csvs_dir()
elif tabletype.lower() == 'metadata':
    directory = get_metadata_csvs_dir()
else:
    raise ValueError("Usage requires table type: 'source' or 'metadata'!")
print(f"** Exploring tables from directory <{directory}> **")

# Tables are looped through, and <number of rows> and <headers> are printed for each.
for filename in sorted(os.listdir(directory)):
    if filename.endswith(".csv"):
        filepath = os.path.join(directory, filename)
        filename = os.path.splitext(filename)[0]

        # Count the number of rows in the csv
        fileObj = open(filepath)
        row_count = sum(1 for row in fileObj)

        # Get the column headers from the csv
        headers = pd.read_csv(filepath, nrows=1).columns.values
        print('%s (%d rows): %s\n' % (filename, row_count, ', '.join(headers)))
        continue
    else:
        continue
