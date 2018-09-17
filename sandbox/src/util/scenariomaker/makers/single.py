from sandbox.util.scenariomaker.makers.makers import Maker


class Single(Maker):
    def __init__(self, decisionspace=None):
        Maker.__init__(self, decisionspace=decisionspace)

    def randomize_betweenbounds(self):
        """Generate random integers for each non-empty (Geo, Agency, Source, BMP) coordinate
        """
        self.animalnametable['Amount'] = self._randomvaluesbetween(lower=self.animalnametable['lowerbound'].values,
                                                                   upper=self.animalnametable['upperbound'].values)
        self.landnametable['Amount'] = self._randomvaluesbetween(lower=self.landnametable['lowerbound'].values,
                                                                 upper=self.landnametable['upperbound'].values)
        self.manurenametable['Amount'] = self._randomvaluesbetween(lower=self.manurenametable['lowerbound'].values,
                                                                   upper=self.manurenametable['upperbound'].values)

        # add to list of scenarios
        self.scenarios_animal.append(self.animalnametable.copy().drop(columns=['lowerbound', 'upperbound']))
        self.scenarios_land.append(self.landnametable.copy().drop(columns=['lowerbound', 'upperbound']))
        self.scenarios_manure.append(self.manurenametable.copy().drop(columns=['lowerbound', 'upperbound']))
