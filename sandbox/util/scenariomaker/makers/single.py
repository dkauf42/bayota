from sandbox.util.scenariomaker.makers.makers import Maker


class Single(Maker):
    def __init__(self, decisionspace=None):
        Maker.__init__(self, decisionspace=decisionspace)

    def randomize_betweenbounds(self):
        """Generate random integers for each non-empty (Geo, Agency, Source, BMP) coordinate
        """
        self.landnametable['amount'] = self._randomvaluesbetween(lower=self.landnametable['lowerbound'].values,
                                                                 upper=self.landnametable['upperbound'].values)
        self.animalnametable['amount'] = self._randomvaluesbetween(lower=self.animalnametable['lowerbound'].values,
                                                                   upper=self.animalnametable['upperbound'].values)
        self.manurenametable['amount'] = self._randomvaluesbetween(lower=self.manurenametable['lowerbound'].values,
                                                                   upper=self.manurenametable['upperbound'].values)

        # rand_matrix = self._randomvaluesbetween(lowermatrix=self.hardlowerboundmatrix.values,
        #                                         uppermatrix=self.hardupperboundmatrix.values)
        # self.scenariomatrix = pd.DataFrame(rand_matrix, index=self.hardupperboundmatrix.index,
        #                                    columns=self.hardupperboundmatrix.columns)
