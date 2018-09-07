from jnotebooks.importing_modules import *
import time
from datetime import datetime

import pyomo.environ as oe

from src.solver_ipopt import SolveAndParse
from src.ipopt.ipopt_parser import IpoptParser

from src.model_makers.costobjective_lrseg import CostObj as CostObj_lrseg
from src.model_makers.costobjective_county import CostObj as CostObj_county
from src.model_makers.loadobjective_lrseg import LoadObj as LoadObj_lrseg
from src.model_makers.loadobjective_county import LoadObj as LoadObj_county

class Study:
    def __init__(self, n=1, objectivetype='costmin',
                 geoscale='lrseg', geoentities=None,
                 baseconstraint=0, saveData2file=False):
        """
        Perform a series of different optimization runs.

        Args:
            n (int): Number of optimization runs to perform in this study
            objectivetype (str): Either 'costmin' or 'loadreductionmax'
            geoscale (str): Either 'county' or 'lrseg'
            geoentities (:obj:`list` of :obj:`str`): the specific lrsegs or counties to include in each run
            baseconstraint (float): Tau or Total_Cost
            saveData2file (bool):

        Examples:
            Examples should be written in doctest format, and should illustrate how
            to use the function.

            >>> print(Study(n=1, objectivetype='costmin', \
                            geoscale='county', \
                            geoentities=['Anne Arundel, MD'], \
                            baseconstraint=5, saveData2file=False))
            [0, 1, 2, 3]

        Definitions
        -----------
            A Trial [from the Google Vizier paper (Golovin et al. 2017)]
        is a list of parameter values, 𝑥, that will lead to a
        single evaluation of 𝑓(𝑥). A trial can be “Completed”, which
        means that it has been evaluated and the objective value
        𝑓(𝑥) has been assigned to it, otherwise it is “Pending”.
        [In other words, each iteration of the solver that calculates a
        single objective value is a trial]
            A Run is a single optimization over a feasible space. Each Run
        contains a configuration describing the feasible space, as well as
        a set of Trials. It is assumed that 𝑓(𝑥) does not change in the
        course of a Run.
            A Study represents a series of runs, with different configurations.
        """
        self.constraintstr = ''
        self.mdl = None
        self.data = None

        starttime_modelinstantiation = time.time()

        # Instantiate a modelmaker object, which itself generates the model and instance data
        modelmaker = self._setup_modelmaker(objectivetype, geoscale)
        self.data = self._set_instance_data(modelmaker, geoscale, geoentities)
        self._setconstraint(self.data, objectivetype, baseconstraint)

        # Tell the modelmaker to create a model instance
        self.mdl = modelmaker.create_concrete(data=self.data)

        timefor_modelinstantiation = time.time() - starttime_modelinstantiation
        print('*model instantiation done* <- it took %f seconds>' % timefor_modelinstantiation)

    def go(self):
        """ Perform a single run - Solve the problem instance """
        self._solve_problem_instance(self.mdl, self.data)

    def _solve_problem_instance(self, mdl, data):
        """

        Args:
            mdl:
            data:

        Returns:

        """
        # ---- Solver details ----
        localsolver = True
        solvername = 'ipopt'

        looptimestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')

        myobj = SolveAndParse(instance=mdl, data=data, localsolver=localsolver, solvername=solvername)

        # ---- Output File Name ----
        output_file_name = os.path.join(projectpath, ''.join(['output/single_CostObj_', looptimestamp, '.iters']))
        IpoptParser().modify_ipopt_options(optionsfilepath='ipopt.opt',
                                           newoutputfilepath=output_file_name)
        # ---- Output Level-of-Detail ----
        # file_print_levels:
        #   4 for just # of iterations, and final objective, infeas,etc. values
        #   6 for summary information about all iterations, but not variable values
        #   8 for variable values at all iterations
        #   10 for all iterations
        IpoptParser().modify_ipopt_options(optionsfilepath='ipopt.opt', newfileprintlevel='8')

        # ---- SOLVE ----
        merged_df = myobj.solve(get_suffixes=False)
        print('\nObjective is: %d' % oe.value(mdl.Total_Cost))

    def _setconstraint(self, data, objectivetype, baseconstraint):
        if objectivetype == 'costmin':
            # ---- Set the total capital available ----
            data.totalcostupperbound = baseconstraint  # e.g. $100,000
            self.constraintstr = str(round(data.totalcostupperbound, 1))
        elif objectivetype == 'loadreductionmax':
            # ---- Set the tau target load ----
            for k in data.tau:
                data.tau[k] = baseconstraint  # e.g. 12% reduction
                self.constraintstr = str(round(data.tau[k], 1))

    def _set_instance_data(self, modelmaker, geoscale, geoentities):
        if geoscale == 'lrseg':
            return modelmaker.load_data(savedata2file=False, lrsegs_list=geoentities)
        elif geoscale == 'county':
            return modelmaker.load_data(savedata2file=False, county_list=geoentities)
        else:
            return None

    def _setup_modelmaker(self, objectivetype, geoscale):
        if objectivetype == 'costmin':
            if geoscale == 'lrseg':
                return CostObj_lrseg()
            elif geoscale == 'county':
                return CostObj_county()
        if objectivetype == 'loadreductionmax':
            if geoscale == 'lrseg':
                return LoadObj_lrseg()
            elif geoscale == 'county':
                return LoadObj_county()
        else:
            return None