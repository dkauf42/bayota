from .makers.single import Single
from .makers.population import Population


class ScenarioMaker(object):
    def __init__(self, decisionspace=None):
        """ Base class for all scenario makers in the optimization engine

        """
        self.single = Single(decisionspace=decisionspace)
        self.population = Population(decisionspace=decisionspace)
