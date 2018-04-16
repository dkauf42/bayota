""" For each table in Source, print out a summary (column headers and number of rows) """
import os
import pandas as pd

directory = os.path.abspath('../../data/test_source/')

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
