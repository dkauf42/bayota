import random
import numpy as np
import pandas as pd
from itertools import product


class Maker(object):
    def __init__(self, decisionspace=None):
        """ Base class for all scenario makers in the optimizer engine

        """
        self.landnametable = decisionspace.land.nametable.copy()
        self.animalnametable = decisionspace.animal.nametable.copy()
        self.manurenametable = decisionspace.manure.nametable.copy()

        self.scenarios_land = []
        self.scenarios_animal = []
        self.scenarios_manure = []

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
    def _randomvaluesbetween(lower, upper):
        if type(lower) != type(upper):
            raise TypeError('Lower and Upper bound objects must be of the same type')

        if isinstance(lower, np.ndarray):
            shapetuple = upper.shape
            return (upper - lower) * np.random.random(shapetuple) + lower
        else:
            raise TypeError('Unrecognized type, not coded for.')
