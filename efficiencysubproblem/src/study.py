import os
import time
import logging
import configparser
import pandas as pd
from datetime import datetime
from collections import OrderedDict

import pyomo.environ as pe

from efficiencysubproblem.src.model_handling.interface import get_loaded_model_handler
from efficiencysubproblem.src.solver_handling.solvehandler import solve_problem_instance

from bayota_settings.base import get_output_dir, get_bayota_version
from bayota_settings.log_setup import root_logger_setup

logger = root_logger_setup()

outdir = get_output_dir()


class Study:
    def __init__(self, *,
                 objectivetype='costmin',
                 geoscale=None, geoentities=None,
                 configfile=None,
                 saveData2file=False):
        """
        Perform a series of different optimization runs.

        Args:
            objectivetype (str): Either 'costmin' or 'loadreductionmax'
            geoscale (str): Either 'county' or 'lrseg'
            geoentities (:obj:`list` of :obj:`str`): the specific lrsegs or counties to include in each run
            saveData2file (bool):

        Attributes:
            modelhandler (obj): A ModelHandler object, which holds the model and data for any particular instance
            geoscale (str): 'county' or 'lrseg'.
            geoentities (:obj:`list` of :obj:`str`): Specific lrsegs or counties to include in each run.
            objectivetype (str): Either 'costmin' or 'loadreductionmax'
            constraintstr (str): String representation of the constraint level.
            numberofrunscompleted (int): Counter for how many runs have been performed so far by this Study object.

        Examples:
            >>> print(Study(objectivetype='costmin', \
                            geoscale='county', \
                            geoentities=['Anne Arundel, MD'], \
                            saveData2file=False))
            ***** Study Details *****
            objective:                costmin
            geographic scale:         county
            # of geographic entities: 1
            current constraint level: not set
            ***************************

        Definitions
        -----------
        [modified from the Google Vizier paper (Golovin et al. 2017)]

            An Iteration is a list of parameter values, 𝑥, that will lead to a
        single evaluation of 𝑓(𝑥). A trial can be “Completed”, which
        means that it has been evaluated and the objective value
        𝑓(𝑥) has been assigned to it, otherwise it is “Pending”.
        [In other words, each iteration of the solver calculates a
        single objective value]

            A Trial is a single optimization over a feasible space. Each Trial
        contains a configuration describing the feasible space, as well as
        a set of iterations. It is assumed that 𝑓(𝑥) does not change in the
        course of a Trial.

            An Experiment is a series of one (or multiple) trial(s),
        with the same geography (sets) and same objective, but different constraints.

            A Study represents a series of one (or multiple) experiment(s),
        with the same geography (sets).
        """

        self.modelhandler = None
        self.constraintstr = 'not set'

        if not configfile:
            self.objectivetype = objectivetype
            self.geoscale = geoscale
            self.geoentities = geoentities
        else:
            config = configparser.ConfigParser()
            config.read(configfile)

            logger.debug('configfile is %s' % configfile)

            self.objectivetype = config['Defaults']['objective']
            self.geoscale = config['Defaults']['scale']
            self.geoentities = config['Defaults']['entities']

        version = get_bayota_version()
        logger.info('----------------------------------------------')
        logger.info('*********** BayOTA version %s *************' % version)
        logger.info('----------------------------------------------\n')
        logger.info('----------------------------------------------')
        logger.info('*********** Study creation started ***********')
        logger.info('***********   [scale=%s]' % self.geoscale)
        logger.info('***********   [entities=%s]' % self.geoentities)
        logger.info('----------------------------------------------')

        # TODO: could add a check here to make sure the PATH variable includes the location of the ipopt solver.

        # Wall time - clock starts.
        starttime_modelinstantiation = time.time()

        # A modelhandler object is instantiated, generating the model and setting instance data.
        self.modelhandler = get_loaded_model_handler(objectivetype, geoscale, geoentities, savedata2file=False)

        # Wall time - clock stops.
        self._endtime_modelinstantiation = time.time()
        timefor_modelinstantiation = self._endtime_modelinstantiation - starttime_modelinstantiation
        logger.info('*model instantiation done* <- it took %f seconds>' % timefor_modelinstantiation)

        self.studystr = ''.join(['study_', self.objectivetype, '_', self.geoscale])
        self.numberofrunscompleted = 0

    def __str__(self):
        """ Custom 'print' that displays the attributes of this Study.
        """
        d = self.__dict__

        formattedstr = "***** Study Details *****\n" \
                       "objective:                %s\n" \
                       "geographic scale:         %s\n" \
                       "# of geographic entities: %s\n" \
                       "current constraint level: %s\n" \
                       "***************************" %\
                       tuple([str(i) for i in [d['objectivetype'],
                                               d['geoscale'],
                                               str(len(d['geoentities'])),
                                               d['constraintstr']
                                               ]
                              ])

        return formattedstr

    def timestr(self):
        """ Return the time of instantation for a Study object as a formatted string """
        d = self.__dict__
        timestr = str(datetime.fromtimestamp(d['_endtime_modelinstantiation']))
        formattedstr = "time of instantiation:    %s" % str(timestr)
        return formattedstr

    def makemodel_from_file(self, modelspecfile):
        pass

    def go(self, *, constraint, fileprintlevel=4):
        """
        Perform a single run - Solve the problem instance.

        Args:
            constraint (float or int): the constraint value (Tau or Total_Cost) to solve for
            fileprintlevel (int): level of detail in the solver ouput files, e.g.
                4 for just # of iterations, and final objective, infeas,etc. values
                6 for summary information about all iterations, but not variable values
                8 for variable values at all iterations
                10 for all iterations

        Returns:
            solver_output_filepath (str): where the iterations' info is saved, if fileprintlevel is set high.
            solution_csv_filepath (str): where the solution info is saved.
            sorteddf_byacres (pd.DataFrame): solution data is stored here for further code manipulation.
            solution_objective (float): numeric objective value of the solution.
            feasible_solution (bool): True or False, as returned by the solver's Termination Condition.
        """

        mdl = self.modelhandler.model

        solver_output_filepath = None
        merged_df = None
        solution_objective = None
        solvetimestamp = ''
        feasible_solution = None

        # Set the constraint level
        self._set_data_constraint_level(constraint)

        if self.objectivetype == 'costmin':
            solver_output_filepath, merged_df, solvetimestamp, feasible_solution = solve_problem_instance(
                self.modelhandler, mdl,
                fileprintlevel=fileprintlevel)
            solution_objective = pe.value(mdl.Total_Cost)
            merged_df['solution_objectives'] = pe.value(mdl.Total_Cost)

            for k in mdl.tau:
                merged_df['tau'] = mdl.tau[k]  # Label this run in the dataframe
                break

            # merged_df['originalload'] = pe.value(mdl.originalload['N'])
            # merged_df['N_pounds_reduced'] = (pe.value(mdl.TargetPercentReduction['N'].body) / 100) * \
            #                                 pe.value(mdl.originalload['N'])

        if self.objectivetype == 'loadreductionmax':
            solver_output_filepath, merged_df, solvetimestamp, feasible_solution = solve_problem_instance(
                self.modelhandler, mdl,
                fileprintlevel=fileprintlevel)
            solution_objective = pe.value(mdl.PercentReduction['N'])
            merged_df['solution_objectives'] = pe.value(mdl.PercentReduction['N'])
            merged_df['totalcostupperbound'] = pe.value(mdl.totalcostupperbound)  # Label this run in the dataframe

        merged_df['feasible'] = feasible_solution

        logger.info('\nObjective is: %d' % solution_objective)

        self._iterate_numberofruns()
        sorteddf_byacres = merged_df.sort_values(by='acres')
        sorteddf_byacres['x'] = list(
            zip(sorteddf_byacres.bmpshortname, sorteddf_byacres.landriversegment,
                sorteddf_byacres.loadsource, sorteddf_byacres.totalannualizedcostperunit))

        solution_csv_filepath = os.path.join(outdir, 'output_' + solvetimestamp + '.csv')
        sorteddf_byacres.to_csv(solution_csv_filepath)

        return solver_output_filepath, solution_csv_filepath, sorteddf_byacres, solution_objective, feasible_solution

    def go_constraintsequence(self, constraints=None, fileprintlevel=4):
        """ Perform multiple runs with different constraints

        Args:
            constraints (list of numeric): the sequence of constraint values (Tau or Total_Cost) to run through & solve
            fileprintlevel (int): level of detail in the solver ouput files, e.g.
                4 for just # of iterations, and final objective, infeas,etc. values
                6 for summary information about all iterations, but not variable values
                8 for variable values at all iterations
                10 for all iterations

        Returns:
            solver_output_filepaths (list of str): where the iterations' info is saved, if fileprintlevel is set high.
            solution_csv_filepath (str): where the solution info is saved.
            alldfs (pd.DataFrame): solution data is stored here for further code manipulation.
            solution_objectives (list of float): numeric objective value of the solution.
            feasible_solution (list of bool): True or False, as returned by the solver's Termination Condition.
        """

        mdl = self.modelhandler.model

        df_list = []
        solution_objectives = OrderedDict()
        feasibility_list = []
        solver_output_filepath = ''
        solver_output_filepaths = []
        merged_df = None
        feasible_solution = None
        solvetimestamp = ''
        loopname = ''

        # Solve problem for each new constraint
        for ii, newconstraint in enumerate(constraints):
            if self.objectivetype == 'costmin':
                # Reassign the target load values (tau)
                for k in mdl.tau:
                    mdl.tau[k] = newconstraint
                    self.constraintstr = str(round(mdl.tau[k].value, 1))
                    logger.info('constraint = %s' % self.constraintstr)

                loopname = ''.join([self.studystr, 'tausequence', str(ii),
                                    '_tau', self.constraintstr])
                solver_output_filepath, merged_df, solvetimestamp, feasible_solution = solve_problem_instance(
                    self.modelhandler, mdl,
                    output_file_str=loopname,
                    fileprintlevel=fileprintlevel)

                # merged_df['originalload'] = pe.value(mdl.originalload['N'])
                # merged_df['N_pounds_reduced'] = (pe.value(mdl.TargetPercentReduction['N'].body) / 100) * \
                #                             pe.value(mdl.originalload['N'])

                # Save this run's objective value in a list
                solution_objectives[newconstraint] = pe.value(mdl.Total_Cost)
                merged_df['solution_objectives'] = pe.value(mdl.Total_Cost)
                merged_df['tau'] = newconstraint  # Label this run in the dataframe
            if self.objectivetype == 'loadreductionmax':
                # Reassign the cost bound values (C)
                mdl.totalcostupperbound = newconstraint
                mdl.totalcostupperbound = mdl.totalcostupperbound
                self.constraintstr = str(round(pe.value(mdl.totalcostupperbound), 1))
                logger.info('constraint = %s' % self.constraintstr)
                loopname = ''.join([self.studystr, 'costboundsequence', str(ii),
                                    '_costbound', self.constraintstr])
                solver_output_filepath, merged_df, solvetimestamp, feasible_solution = solve_problem_instance(
                    self.modelhandler, mdl,
                    output_file_str=loopname,
                    fileprintlevel=fileprintlevel)

                # Save this run's objective value in a list
                solution_objectives[newconstraint] = pe.value(mdl.PercentReduction['N'])
                merged_df['solution_objectives'] = pe.value(mdl.PercentReduction['N'])
                merged_df['totalcostupperbound'] = newconstraint  # Label this run in the dataframe

            self._iterate_numberofruns()

            merged_df['feasible'] = feasible_solution
            feasibility_list.append(feasible_solution)

            sorteddf_byacres = merged_df.sort_values(by='acres')
            # Save all of the solutions in a list
            df_list.append(sorteddf_byacres)
            solver_output_filepaths.append(solver_output_filepath)

        # Save the results to a .csv file
        alldfs = pd.concat(df_list, ignore_index=True)
        alldfs['x'] = list(
            zip(alldfs.bmpshortname, alldfs.landriversegment, alldfs.loadsource, alldfs.totalannualizedcostperunit))

        solution_csv_filepath = os.path.join(outdir, 'output_' + loopname + '_' + solvetimestamp + '.csv')
        alldfs.to_csv(solution_csv_filepath)

        return solver_output_filepaths, solution_csv_filepath, alldfs, solution_objectives, feasibility_list

    def _set_data_constraint_level(self, baseconstraint):
        # Check whether multiple runs are required
        if isinstance(baseconstraint, list):
            baseconstraint = baseconstraint[0]

        if self.objectivetype == 'costmin':
            # ---- Set the tau target load, e.g. 12% reduction ----
            for k in self.modelhandler.model.tau:
                self.modelhandler.model.tau[k] = baseconstraint
                self.constraintstr = str(round(pe.value(self.modelhandler.model.tau[k]), 1))
        elif self.objectivetype == 'loadreductionmax':
            # ---- Set the total capital available, e.g. $100,000 ----
            self.modelhandler.model.totalcostupperbound = baseconstraint
            self.constraintstr = str(round(pe.value(self.modelhandler.model.totalcostupperbound), 1))

    def _iterate_numberofruns(self):
        self.numberofrunscompleted += 1

