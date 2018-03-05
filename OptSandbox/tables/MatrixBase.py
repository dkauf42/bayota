import pandas as pd
from itertools import product
from tqdm import tqdm  # Loop progress indicator module


class MatrixBase:
    def __init__(self, name='', row_indices=None, column_names=None):
        """A wrapper class for a possibility matrix needed for an optinstance"""
        self.name = name

        if (row_indices is None) | (column_names is None):
            self.matrix = pd.DataFrame()
        else:
            # generate the skeleton of a matrix with sorted rows and columns
            df = pd.DataFrame(index=row_indices, columns=column_names)
            df.sort_index(axis=0, inplace=True, sort_remaining=True)
            df.sort_index(axis=1, inplace=True, sort_remaining=True)
            self.matrix = df

    def __getitem__(self, item):
        return getattr(self, item)

    @staticmethod
    def mark_eligible_coordinates(dataframe=None, bmpdict=None):
        """ Indicate the BMPs that are possible on each load source in the table with a '1' """
        loadsourceindex = dataframe.index.names.index('LoadSource')
        for index, row in tqdm(dataframe.iterrows(), total=len(dataframe.index)):  # iterate through the load sources
            bmplist_for_this_loadsource = bmpdict[row.name[loadsourceindex]]
            row.loc[bmplist_for_this_loadsource] = 1  # Mark eligible BMPs for each load source w/a '1' instead of NaN

    @staticmethod
    def expand_grid(data_dict):
        """ Short method for generating all the combinations of values from a dictionary input"""
        rows = product(*data_dict.values())
        return pd.DataFrame.from_records(rows, columns=data_dict.keys())
