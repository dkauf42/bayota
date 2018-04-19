import random
import pandas as pd
import numpy as np
from itertools import product

import pyDOE


class PopulationMaker:
    def __init__(self):
        self.land = None
        self.animal = None
        self.manure = None

    def initialize_from_decisionspace(self, land=None, animal=None, manure=None):
        self.land = land.copy()
        self.animal = animal.copy()
        self.manure = manure.copy()

    def generate_latinhypercube(self):
        """Generate random integers for each non-empty (Geo, Agency, Source, BMP) coordinate
        """

        landvectors = self.generate_latinhypercube_from_bounds(lower=self.land['lowerbound'].values,
                                                               upper=self.land['upperbound'].values)
        animalvectors = self.generate_latinhypercube_from_bounds(lower=self.animal['lowerbound'].values,
                                                                 upper=self.animal['upperbound'].values)
        manurevectors = self.generate_latinhypercube_from_bounds(lower=self.manure['lowerbound'].values,
                                                                 upper=self.manure['upperbound'].values)

        # self.land['amount'] = self._randomvaluesbetween(lower=self.land['lowerbound'].values,
        #                                                 upper=self.land['upperbound'].values)
        # self.animal['amount'] = self._randomvaluesbetween(lower=self.animal['lowerbound'].values,
        #                                                   upper=self.animal['upperbound'].values)
        # self.manure['amount'] = self._randomvaluesbetween(lower=self.manure['lowerbound'].values,
        #                                                   upper=self.manure['upperbound'].values)

        # rand_matrix = self._randomvaluesbetween(lowermatrix=self.hardlowerboundmatrix.values,
        #                                         uppermatrix=self.hardupperboundmatrix.values)
        # self.scenariomatrix = pd.DataFrame(rand_matrix, index=self.hardupperboundmatrix.index,
        #                                    columns=self.hardupperboundmatrix.columns)

    def generate_latinhypercube_from_bounds(self, lower, upper):
        if type(lower) != type(upper):
            raise TypeError('Lower and Upper bound objects must be of the same type')
        if len(lower) != len(upper):
            raise ValueError('Lower and Upper bound objects must be of the same length')

        lhd = pyDOE.lhs(n=len(upper), samples=10)

        if isinstance(lower, np.ndarray):
            return (upper - lower) * lhd + lower
        else:
            raise TypeError('Unrecognized type, not coded for.')



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

