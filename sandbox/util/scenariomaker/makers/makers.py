import os
import random
import numpy as np
import pandas as pd
from itertools import product

from sandbox.__init__ import get_outputdir

writedir = get_outputdir()


class Maker(object):
    def __init__(self, decisionspace=None):
        """ Base class for all scenario makers in the optimizer engine

        """
        self.animalnametable = decisionspace.animal.nametable.copy()
        self.landnametable = decisionspace.land.nametable.copy()
        self.manurenametable = decisionspace.manure.nametable.copy()

        # self.scenarios = []

        self.scenarios_animal = []
        self.scenarios_land = []
        self.scenarios_manure = []

    def __iter__(self):
        """ Generator to return the scenario objects, e.g. in For loops """
        # self.scenarios = [self.scenarios_animal, self.scenarios_land, self.scenarios_manure]
        for x, y in zip(['animal', 'land', 'manure'],
                        [self.scenarios_animal, self.scenarios_land, self.scenarios_manure]):
            yield x, y

    def write_to_tab_delimited_txt_file(self):
        print('Makers.write_to_tab_delimited_txt_file()')
        print(self.scenarios_land)
        # columns that are ids are translated to names, and scenarios are written to file.
        i = 0
        for df in self.scenarios_land:
            print('Makers.write_to_tab_delimited_txt_file()')
            df.to_csv(os.path.join(writedir, 'testwrite_CASTscenario_land_%d.txt' % i),
                      sep='\t', header=True, index=False, line_terminator='\r\n')
            i += 1

        i = 0
        for df in self.scenarios_animal:
            df.to_csv(os.path.join(writedir, 'testwrite_CASTscenario_animal_%d.txt' % i),
                      sep='\t', header=True, index=False, line_terminator='\r\n')
            i += 1

        i = 0
        for df in self.scenarios_manure:
            df.to_csv(os.path.join(writedir, 'testwrite_CASTscenario_manure_%d.txt' % i),
                      sep='\t', header=True, index=False, line_terminator='\r\n')
            i += 1


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
