import pyomo.environ as oe
from pyomo.opt import SolverFactory, SolverManagerFactory

from efficiencysubproblem.src.solution_handling.solutionhandler import *


class SolveHandler:
    def __init__(self, instance=None, localsolver=False, solvername=''):

        self.instance = instance
        self.solvername = solvername
        self.localsolver = localsolver

    def solve(self, logfilename='logfile_loadobjective.log', get_suffixes=True):
        if self.localsolver:
            solver = SolverFactory(self.solvername)

            if get_suffixes:
                self.instance.dual = oe.Suffix(direction=oe.Suffix.IMPORT)
                self.instance.ipopt_zL_out = oe.Suffix(direction=oe.Suffix.IMPORT)
                self.instance.ipopt_zU_out = oe.Suffix(direction=oe.Suffix.IMPORT)
                setattr(self.instance, 'lambda', oe.Suffix(direction=oe.Suffix.IMPORT))  # use setattr because 'lambda' is reserved keyword

            results = solver.solve(self.instance, tee=True, symbolic_solver_labels=True,
                                   keepfiles=True, logfile=logfilename)
        else:
            opt = SolverFactory("cbc")
            solver_manager = SolverManagerFactory('neos')

            self.instance.dual = oe.Suffix(direction=oe.Suffix.IMPORT)
            self.instance.rc = oe.Suffix(direction=oe.Suffix.IMPORT)
            self.instance.dual = oe.Suffix(direction=oe.Suffix.IMPORT_EXPORT)
            # self.instance.slack = oe.Suffix(direction=oe.Suffix.IMPORT)

            opt.options["display_width"] = 170
            opt.options["display"] = '_varname, _var.rc, _var.lb, _var, _var.ub, _var.slack'
            results = solver_manager.solve(self.instance, opt=opt, solver=self.solvername, logfile=logfilename)

            results.write()

        # self.instance.display()

        return self.instance
