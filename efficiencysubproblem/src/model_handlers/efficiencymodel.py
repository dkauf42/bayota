import pyomo.environ as oe

from efficiencysubproblem.src.data_handlers.county import County


class EfficiencyModel:
    def __init__(self, saveData2file=False, tau=12,
                 instance=None, data=None, localsolver=False, solvername=''):
        pass

    def load_data(self):
        pass

    def create_concrete(self, data):
        pass