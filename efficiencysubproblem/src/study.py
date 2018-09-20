import time
import pandas as pd
from datetime import datetime
from collections import OrderedDict

import pyomo.environ as oe

from efficiencysubproblem.jnotebooks.importing_modules import *

from efficiencysubproblem.src.solver_handlers.solve_triggerer import SolveAndParse
from efficiencysubproblem.src.solution_handlers.ipopt_parser import IpoptParser

from efficiencysubproblem.src.model_handlers.costobjective_lrseg import CostObj as CostObj_lrseg
from efficiencysubproblem.src.model_handlers.costobjective_county import CostObj as CostObj_county
from efficiencysubproblem.src.model_handlers.loadobjective_lrseg import LoadObj as LoadObj_lrseg
from efficiencysubproblem.src.model_handlers.loadobjective_county import LoadObj as LoadObj_county

class Study:
    def __init__(self, objectivetype='costmin',
                 geoscale='county', geoentities=None,
                 baseconstraint=5, saveData2file=False):
        """
        Perform a series of different optimization runs.

        Args:
            objectivetype (str): Either 'costmin' or 'loadreductionmax'
            geoscale (str): Either 'county' or 'lrseg'
            geoentities (:obj:`list` of :obj:`str`): the specific lrsegs or counties to include in each run
            baseconstraint (float): Tau or Total_Cost
            saveData2file (bool):

        Examples:
            Examples should be written in doctest format, and should illustrate how
            to use the function.

            >>> print(Study(objectivetype='costmin', \
                            geoscale='county', \
                            geoentities=['Anne Arundel, MD'], \
                            baseconstraint=5, saveData2file=False))
            [0, 1, 2, 3]

        Definitions
        -----------
            A Trial is a list of parameter values, 𝑥, that will lead to a
        single evaluation of 𝑓(𝑥). A trial can be “Completed”, which
        means that it has been evaluated and the objective value
        𝑓(𝑥) has been assigned to it, otherwise it is “Pending”.
        [from the Google Vizier paper (Golovin et al. 2017)]
        [In other words, each iteration of the solver that calculates a
        single objective value is a trial]
            A Run is a single optimization over a feasible space. Each Run
        contains a configuration describing the feasible space, as well as
        a set of Trials. It is assumed that 𝑓(𝑥) does not change in the
        course of a Run.
            A Study represents a series of runs, with different configurations.
        """
        if not geoentities:
            raise ValueError('Geoentities must be specified')

        self.constraintstr = ''
        self.mdl = None
        self.data = None
        self.geoscale = geoscale
        self.geoentities = geoentities
        self.objectivetype = objectivetype

        starttime_modelinstantiation = time.time()

        # Instantiate a modelhandler object, which itself generates the model and instance data
        modelhandler = self._setup_modelhandler()
        # Set instance Data
        if self.geoscale == 'lrseg':
            self.data = modelhandler.load_data(savedata2file=False, lrsegs_list=self.geoentities)
        elif self.geoscale == 'county':
            self.data = modelhandler.load_data(savedata2file=False, county_list=self.geoentities)
        else:
            raise ValueError('unrecognized "geoscale"')
        # Set the base constraint level
        self._setconstraint(self.data, baseconstraint)

        # Tell the modelhandler to create a model instance
        self.mdl = modelhandler.create_concrete(data=self.data)

        self.endtime_modelinstantiation = time.time()
        timefor_modelinstantiation = self.endtime_modelinstantiation - starttime_modelinstantiation
        print('*model instantiation done* <- it took %f seconds>' % timefor_modelinstantiation)

        self.studystr = ''.join(['study_', self.objectivetype, '_',
                                 self.geoscale])

        self.numberofrunscompleted = 0

    def __str__(self):
        """ Custom 'print' that displays the attributes of this Study.
        """
        d = self.__dict__

        timestr = str(datetime.fromtimestamp(d['endtime_modelinstantiation']))

        formattedstr = "\n***** Study Details *****\n" \
                       "objective:                %s\n" \
                       "geographic scale:         %s\n" \
                       "# of geographic entities: %s\n" \
                       "current constraint level: %s\n" \
                       "time of instantiation:    %s\n" \
                       "***************************\n" %\
                       tuple([str(i) for i in [d['objectivetype'],
                                               d['geoscale'],
                                               str(len(d['geoentities'])),
                                               d['constraintstr'],
                                               timestr
                                               ]
                              ])

        return formattedstr

    def go(self):
        """ Perform a single run - Solve the problem instance """
        output_file_name, merged_df, solvetimestamp = self._solve_problem_instance(self.mdl, self.data)

        return output_file_name, merged_df

    def go_constraintsequence(self, constraints=None):
        """ Perform multiple runs with different constraints """

        df_list = []
        solution_objectives = OrderedDict()
        output_file_names = []

        # Solve problem for each new constraint
        for ii, newconstraint in enumerate(constraints):
            if self.objectivetype == 'costmin':
                # Reassign the target load values (tau)
                for k in self.data.tau:
                    self.mdl.tau[k] = newconstraint
                    self.constraintstr = str(round(self.mdl.tau[k].value, 1))
                    print(self.constraintstr)

                loopname = ''.join([self.studystr, 'tausequence', str(ii),
                                    '_tau', self.constraintstr])
                output_file_name, merged_df, solvetimestamp = self._solve_problem_instance(self.mdl, self.data,
                                                                                           output_file_str=loopname)
                # Save this run's objective value in a list
                solution_objectives[newconstraint] = oe.value(self.mdl.Total_Cost)
                merged_df['solution_objectives'] = oe.value(self.mdl.Total_Cost)
                merged_df['tau'] = newconstraint  # Label this run in the dataframe
            if self.objectivetype == 'loadreductionmax':
                # Reassign the cost bound values (C)
                self.data.totalcostupperbound = newconstraint
                self.mdl.totalcostupperbound = self.data.totalcostupperbound
                self.constraintstr = str(round(self.data.totalcostupperbound, 1))
                print(self.constraintstr)
                loopname = ''.join([self.studystr, 'costboundsequence', str(ii),
                                    '_costbound', self.constraintstr])
                output_file_name, merged_df, solvetimestamp = self._solve_problem_instance(self.mdl, self.data,
                                                                                           output_file_str=loopname)
                # Save this run's objective value in a list
                solution_objectives[newconstraint] = oe.value(self.mdl.PercentReduction['N'])
                merged_df['solution_objectives'] = oe.value(self.mdl.PercentReduction['N'])
                merged_df['totalcostupperbound'] = newconstraint  # Label this run in the dataframe

            sorteddf_byacres = merged_df.sort_values(by='acres')
            # Save all of the solutions in a list
            df_list.append(sorteddf_byacres)
            output_file_names.append(output_file_name)

        # Save the results to a .csv file
        alldfs = pd.concat(df_list, ignore_index=True)
        alldfs['x'] = list(
            zip(alldfs.bmpshortname, alldfs.landriversegment, alldfs.loadsource, alldfs.totalannualizedcostperunit))
        filenamestr = ''.join(['output/output_', loopname, '_', solvetimestamp, '.csv'])
        alldfs.to_csv(os.path.join(projectpath, filenamestr))

        return output_file_names, alldfs

    def _solve_problem_instance(self, mdl, data, randomstart=False, output_file_str=''):
        """

        Args:
            mdl:
            data:
            randomstart: If False, than the ipopt default is used.. zero for each variable

        Returns:

        """
        # ---- Solver details ----
        localsolver = True
        solvername = 'ipopt'

        if randomstart:
            import random
            # reinitialize the variables
            for k in mdl.x:
                mdl.x[k] = round(random.uniform(0, 6000), 2)

        solvetimestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')

        myobj = SolveAndParse(instance=mdl, data=data, localsolver=localsolver, solvername=solvername)

        # ---- Output File Name ----
        if not output_file_str:
            output_file_name = os.path.join(projectpath, ''.join(['output/output_', solvetimestamp, '.iters']))
        else:
            output_file_name = os.path.join(projectpath, ''.join(['output/output_', output_file_str, '_', solvetimestamp, '.iters']))
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

        return output_file_name, merged_df, solvetimestamp

    def _setconstraint(self, data, baseconstraint):
        if self.objectivetype == 'costmin':
            # ---- Set the total capital available ----
            data.totalcostupperbound = baseconstraint  # e.g. $100,000
            self.constraintstr = str(round(data.totalcostupperbound, 1))
        elif self.objectivetype == 'loadreductionmax':
            # ---- Set the tau target load ----
            for k in data.tau:
                data.tau[k] = baseconstraint  # e.g. 12% reduction
                self.constraintstr = str(round(data.tau[k], 1))

    def _setup_modelhandler(self):
        if self.objectivetype == 'costmin':
            if self.geoscale == 'lrseg':
                return CostObj_lrseg()
            elif self.geoscale == 'county':
                return CostObj_county()
        if self.objectivetype == 'loadreductionmax':
            if self.geoscale == 'lrseg':
                return LoadObj_lrseg()
            elif self.geoscale == 'county':
                return LoadObj_county()
        else:
            return None