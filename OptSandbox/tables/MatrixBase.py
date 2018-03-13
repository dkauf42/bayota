import random
import pandas as pd
import numpy as np
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

        self.hardupperboundmatrix = pd.DataFrame()
        self.hardlowerboundmatrix = pd.DataFrame()

        self.scenariomatrix = pd.DataFrame()

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

    def get_list_of_bmps(self):
        return self.eligibleparametermatrix.columns.tolist()

    def get_list_of_eligible_bmps(self):
        booleanwhethercolsareallnans = self.eligibleparametermatrix.apply(lambda x: x.isnull().all(), axis=0)
        return self.eligibleparametermatrix.columns[~booleanwhethercolsareallnans].tolist()

    def get_list_of_max_hubs_for_bmps(self):
        return self.hardupperboundmatrix.max(axis=0)

    def get_list_of_min_hlbs_for_bmps(self):
        # TODO: check the lower bound functions for correctness
        return self.hardupperboundmatrix.min(axis=0)

    def randomize_belowhub(self):
        """Generate random integers for each non-empty (Geo, Agency, Source, BMP) coordinate

        Parameters:
            dataframe (pandas dataframe):
        """
        #print('MatrixBase.randomize_belowhub: H.U.B. matrix...')
        #print(self.hardupperboundmatrix)

        #print('MatrixBase.randomize_belowhub: randomize between returns...')
        retval = self._randomvaluesbetween(lowermatrix=self.hardlowerboundmatrix.values,
                                           uppermatrix=self.hardupperboundmatrix.values)
        retval = pd.DataFrame(retval, index=self.hardupperboundmatrix.index,
                                      columns=self.hardupperboundmatrix.columns)
        #print(retval)
        self.scenariomatrix = retval

        #howmanytoreplace = (dataframe == 1).sum().sum()
        #dataframe[dataframe == 1] = random.sample(range(1, howmanytoreplace+1), howmanytoreplace)

    @staticmethod
    def expand_grid(data_dict):
        """ Short method for generating all the combinations of values from a dictionary input"""
        rows = product(*data_dict.values())
        return pd.DataFrame.from_records(rows, columns=data_dict.keys())

    @staticmethod
    def _rand_integers(dataframe):
        howmanytoreplace = (dataframe == 1).sum().sum()
        dataframe[dataframe == 1] = random.sample(range(1, howmanytoreplace+1), howmanytoreplace)

    @staticmethod
    def _rand_matrix(dataframe):
        np.random.random(dataframe.shape)

    @staticmethod
    def _randomvaluesbetween(lowermatrix, uppermatrix):
        m, n = uppermatrix.shape
        print('MatrixBase._randomvaluesbetween(): m=%d, n=%d' % (m, n))
        print(np.random.random((m, n)))
        print((uppermatrix - lowermatrix))
        return (uppermatrix - lowermatrix) * np.random.random((m, n)) + lowermatrix
