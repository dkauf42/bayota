import random
import pandas as pd
import numpy as np
from itertools import product
from tqdm import tqdm  # Loop progress indicator module


class ScenarioGenerator:
    def __init__(self, name='', row_indices=None, column_names=None):
        pass

    def randomize_belowhub(self):
        """Generate random integers for each non-empty (Geo, Agency, Source, BMP) coordinate

        Parameters:
            dataframe (pandas dataframe):
        """
        # rand_matrix = self._randomvaluesbetween(lowermatrix=self.hardlowerboundmatrix.values,
        #                                         uppermatrix=self.hardupperboundmatrix.values)
        # self.scenariomatrix = pd.DataFrame(rand_matrix, index=self.hardupperboundmatrix.index,
        #                                    columns=self.hardupperboundmatrix.columns)

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
        return (uppermatrix - lowermatrix) * np.random.random((m, n)) + lowermatrix