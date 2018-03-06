import pandas as pd
from itertools import product
from tqdm import tqdm  # Loop progress indicator module


class MatrixBase:
    def __init__(self, name='', row_indices=None, column_names=None):
        """A wrapper class for a possibility parametermatrix needed for an optinstance"""
        self.name = name

        if (row_indices is None) | (column_names is None):
            self.emptyparametermatrix = pd.DataFrame()
        else:
            # generate the skeleton of a emptyparametermatrix with sorted rows and columns
            df = pd.DataFrame(index=row_indices, columns=column_names)

            #  Don't sort ya'ads because they need to match the ya'ad table
            # Sorting the BMPs(columns) should be fine, but I don't think there's any reason to do so.
            #df.sort_index(axis=1, inplace=True, sort_remaining=True)

            self.emptyparametermatrix = df

        self.eligibleparametermatrix = pd.DataFrame()

    def __getitem__(self, item):
        return getattr(self, item)

    def mark_eligible_coordinates(self, bmpdict=None):
        """ Indicate the BMPs that are possible on each load source in the table with a '1' """
        self.eligibleparametermatrix = self.emptyparametermatrix.copy()
        loadsourceindex = self.eligibleparametermatrix.index.names.index('LoadSource')
        for index, row in tqdm(self.eligibleparametermatrix.iterrows(), total=len(self.eligibleparametermatrix.index)):
            # iterate through the load sources
            bmplist_for_this_loadsource = bmpdict[row.name[loadsourceindex]]
            row.loc[bmplist_for_this_loadsource] = 1  # Mark eligible BMPs for each load source w/a '1' instead of NaN

    @staticmethod
    def expand_grid(data_dict):
        """ Short method for generating all the combinations of values from a dictionary input"""
        rows = product(*data_dict.values())
        return pd.DataFrame.from_records(rows, columns=data_dict.keys())
