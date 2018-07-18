import pyomo.environ as oe
from pyomo.opt import SolverFactory, SolverManagerFactory

from util.solution_wrangler import *


class SolveAndParse:
    def __init__(self, instance=None, data=None, localsolver=False, solvername=''):

        self.instance = instance
        self.data = data
        self.solvername = solvername
        self.localsolver = localsolver

    def solve(self):
        if self.localsolver:
            solver = SolverFactory(self.solvername)

            self.instance.dual = oe.Suffix(direction=oe.Suffix.IMPORT)
            self.instance.ipopt_zL_out = oe.Suffix(direction=oe.Suffix.IMPORT)
            self.instance.ipopt_zU_out = oe.Suffix(direction=oe.Suffix.IMPORT)

            results = solver.solve(self.instance, tee=True, symbolic_solver_labels=True, keepfiles=True,
                                   logfile='logfile_loadobjective.log')
        else:
            opt = SolverFactory("cbc")
            solver_manager = SolverManagerFactory('neos')

            # self.instance.dual = oe.Suffix(direction=oe.Suffi}x.IMPORT)
            self.instance.rc = oe.Suffix(direction=oe.Suffix.IMPORT)
            self.instance.dual = oe.Suffix(direction=oe.Suffix.IMPORT_EXPORT)
            # self.instance.slack = oe.Suffix(direction=oe.Suffix.IMPORT)

            opt.options["display_width"] = 170
            opt.options["display"] = '_varname, _var.rc, _var.lb, _var, _var.ub, _var.slack'
            results = solver_manager.solve(self.instance, opt=opt, solver=self.solvername, logfile='logfile_loadobjective.log')

            results.write()

        # self.instance.display()

        # Parse out the Lagrange Multipliers
        zL_df = get_lagrangemult_df(self.instance)
        # Parse out only the optimal variable values that are nonzero
        nzvnames, nzvvalues = get_nonzero_var_names_and_values(self.instance)
        nonzerodf = get_nonzero_var_df(self.instance, addcosttbldata=self.data.costsubtbl)
        merged_df = zL_df.merge(nonzerodf,
                                how='right',
                                on=['bmpshortname', 'landriversegment', 'loadsource'])

        return merged_df
