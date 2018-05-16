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
        numsamples = 2
        self.scenarios_land = self._generate_latinhypercube_from_table(table=self.landnametable,
                                                                       numsamples=numsamples,
                                                                       tablename='land')
        self.scenarios_animal = self._generate_latinhypercube_from_table(table=self.animalnametable,
                                                                         numsamples=numsamples,
                                                                         tablename='animal')
        self.scenarios_manure = self._generate_latinhypercube_from_table(table=self.manurenametable,
                                                                         numsamples=numsamples,
                                                                         tablename='manure')

    def _generate_latinhypercube_from_table(self, table, numsamples, tablename):
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

            # # Apply Softmax to Animals
            # if tablename == 'animal':
            #     keycols = ['AgencyCode', 'BmpShortname', 'GeographyName', 'AnimalGroup', 'LoadSourceGroup']
            #
            #     # sumToOneGroups = thisdf.groupby(keycols)
            #     # sumToOneGroups = self.softmax(sumToOneGroups['Amount'])
            #     print(thisdf.head())
            #     g = thisdf.groupby(keycols)
            #     # adskfjhsdfkhadkh
            #     for key, item in g:
            #         print(g.get_group(key), "\n\n")
            #
            #     thisdf['Amount'] = g['Amount'].transform(lambda x: self.softmax(x))
            #     # g['Amount'] = self.softmax(g['Amount'])
            #
            #     # thisdf['Amount'] = thisdf[keycols].map(g['Amount'])

            dflist.append(thisdf)

        return dflist

    def add_bmptype_column(self, jeeves):
        for i in range(len(self.scenarios_animal)):
            self.scenarios_animal[i] = jeeves.bmp. \
                appendBmpType_to_table_with_bmpshortnames(self.scenarios_animal[i])
        for i in range(len(self.scenarios_land)):
            self.scenarios_land[i] = jeeves.bmp. \
                appendBmpType_to_table_with_bmpshortnames(self.scenarios_land[i])
        for i in range(len(self.scenarios_manure)):
            self.scenarios_manure[i] = jeeves.bmp. \
                appendBmpType_to_table_with_bmpshortnames(self.scenarios_manure[i])

