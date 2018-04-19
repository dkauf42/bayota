import random
import pandas as pd
import numpy as np
from itertools import product

import pyDOE


class PopulationMaker:
    def __init__(self):
        self.dsland = None
        self.dsanimal = None
        self.dsmanure = None

        self.scenarios_land = []
        self.scenarios_animal = []
        self.scenarios_manure = []

    def initialize_from_decisionspace(self, land=None, animal=None, manure=None):
        self.dsland = land.copy()
        self.dsanimal = animal.copy()
        self.dsmanure = manure.copy()

    def generate_latinhypercube(self):
        """Conduct a latin hypercube sampling from within the lower/upper bounds
        """
        # Conduct a latin hypercube sampling from within the lower/upper bounds
        numsamples = 10
        self.scenarios_land = self._generate_latinhypercube_from_table(table=self.dsland, numsamples=numsamples)
        self.scenarios_animal = self._generate_latinhypercube_from_table(table=self.dsanimal, numsamples=numsamples)
        self.scenarios_manure = self._generate_latinhypercube_from_table(table=self.dsmanure, numsamples=numsamples)

    @staticmethod
    def _generate_latinhypercube_from_table(table, numsamples):
        lhd = pyDOE.lhs(n=len(table.upperbound), samples=numsamples)
        # lower and upper bound vectors are tiled so that they match the shape of the latin hypercube
        lower = np.tile(table.lowerbound, (numsamples, 1))
        upper = np.tile(table.upperbound, (numsamples, 1))
        # samples in the 0:1 range are rescaled to the lower:upper range
        lhd_full = ((upper - lower) * lhd + lower).transpose()
        # Create new dataframes, each with a new 'amount' column containing each hypercube sample
        dflist = []
        for i in range(0, numsamples):
            thisdf = table.copy().drop(columns=['lowerbound', 'upperbound'])
            thisdf['Amount'] = lhd_full[:, i]
            dflist.append(thisdf)

        return dflist

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

