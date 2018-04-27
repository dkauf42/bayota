import collections
import pandas as pd

from sandbox.util.jeeves import Jeeves
from .spaces.animal import Animal
from .spaces.land import Land
from .spaces.manure import Manure


class DecisionSpace(object):
    def __init__(self):
        """ Base class for all decision spaces in the optimizer engine
        Represent the variables that make up the decision space along with their upper and lower bounds.

        A DecisionSpace holds:
            - tables with IDs and names for lrsegs, counties, agencies, sectors, loadsources, BMPs
        A DecisionSpace can perform these actions:
            - construct itself from a specified geography or geoagencysector table
            - QC itself

        """
        # SourceHooks
        jeeves = self.load_queries()

        self.animal = Animal(jeeves=jeeves)
        self.land = Land(jeeves=jeeves)
        self.manure = Manure(jeeves=jeeves)

    @staticmethod
    def load_queries():
        # SourceHooks
        return Jeeves()
