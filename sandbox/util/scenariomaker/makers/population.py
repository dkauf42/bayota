import numpy as np

import pyDOE

from sandbox.util.scenariomaker.makers.makers import Maker


class Population(Maker):
    def __init__(self, decisionspace=None):
        Maker.__init__(self, decisionspace=decisionspace)

    def generate_latinhypercube(self):
        """Conduct a latin hypercube sampling from within the lower/upper bounds
        """
        # Conduct a latin hypercube sampling from within the lower/upper bounds
        numsamples = 10
        self.scenarios_land = self._generate_latinhypercube_from_table(table=self.landnametable, numsamples=numsamples)
        self.scenarios_animal = self._generate_latinhypercube_from_table(table=self.animalnametable, numsamples=numsamples)
        self.scenarios_manure = self._generate_latinhypercube_from_table(table=self.manurenametable, numsamples=numsamples)

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

