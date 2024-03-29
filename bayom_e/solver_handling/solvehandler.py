""" Set up optimization solver, send solve commands, and perform checks.
"""

# Generic/Built-in
import os
import re
import sys
import time
import logging
import fileinput
import tempfile
from datetime import datetime
import pyutilib
import traceback

# Computation
import pandas as pd
import pyomo.environ as pyo
from pyomo.opt import SolverFactory, SolverManagerFactory, SolverStatus, TerminationCondition

# BAYOTA
from bayom_e.config import PROJECT_DIR
from bayom_e.solution_handling.solutionhandler import SolutionHandler, \
    initial_solution_parse_to_dataframe
from bayota_util.infeasible import *
from bayota_settings.base import get_output_dir, get_raw_data_dir
from castjeeves.jeeves import Jeeves

logger = logging.getLogger(__name__)


class SolveHandler:
    def __init__(self, instance=None, localsolver=False, solvername=''):
        self.jeeves = Jeeves()

        self.instance = instance
        self.solvername = solvername
        self.localsolver = localsolver

        self.solver_path = self.get_solver_path()

        # If the solver executable is found on PATH, then we check for solver options file in same dir.
        if not not self.solver_path:
            self.options_file_path = os.path.join(os.path.dirname(self.solver_path), 'ipopt.opt')

            try:
                open(self.options_file_path, 'x')
            except FileExistsError:
                pass  # 'x': exclusive creation - operation fails if file already exists, but creates it if it does not.

            logger.debug('Solver_Path====%s' % self.options_file_path)

        else:
            self.options_file_path = None

    def get_solver_path(self):
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(self.solvername)
        if fpath:
            if is_exe(self.solvername):
                return self.solvername
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, self.solvername)
                if is_exe(exe_file):
                    return exe_file

        return None

    def modify_ipopt_options(self, newoutputfilepath='', newfileprintlevel=''):
        rx_kv = re.compile(r'''^(?P<key>[\w._]+)\s(?P<value>[^\s]+)''')

        def _parse_line(string):
            """
            Do a regex search against all defined regexes and
            return the key and match result of the first matching regex

            """
            iterator = rx_kv.finditer(string)

            row = None
            for match in iterator:
                if match:
                    row = {'key': match.group('key'),
                           'value': match.group('value')
                           }

            return row

        for line in fileinput.FileInput(self.options_file_path, inplace=1):
            parsed = _parse_line(line)
            if parsed:
                if parsed['key'] == 'output_file':
                    if not not newoutputfilepath:
                        line = line.replace(parsed['value'], newoutputfilepath)
                if parsed['key'] == 'file_print_level':
                    if not not newfileprintlevel:
                        line = line.replace(parsed['value'], str(newfileprintlevel))
            sys.stdout.write(line)

    def basic_solve(self, mdl, fileprintlevel=4,
                    translate_to_cast_format=False, solverlogfile=None,
                    solveritersfile=None):
        """

        Args:
            mdl:
            output_file_str:
            fileprintlevel:
            translate_to_cast_format:

        Returns:

        """
        # ---- Solver details ----
        localsolver = True
        solvername = 'ipopt'

        solver_path, options_file_path = get_solver_paths(solvername)
        logger.debug(f"using solver <{solvername}> at path <{solver_path}>")

        solvetimestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if not solverlogfile:
            # ---- Output (Iterations and IPOPT Log) Filenames ----
            if not solveritersfile:
                output_file_name = os.path.join(get_output_dir(), 'output_' + solvetimestamp + '.iters')
            else:
                output_file_name = solveritersfile
            ipopt_log_file = os.path.join(get_output_dir(), 'ipopt_logfile_' + solvetimestamp + '.log')
        else:
            output_file_name = solveritersfile
            ipopt_log_file = solverlogfile

        # ---- SOLVE ----
        get_suffixes = False
        solved_instance, solved_results, feasible = solve(localsolver,
                                                          solvername,
                                                          mdl,
                                                          logfilename=ipopt_log_file,
                                                          get_suffixes=get_suffixes,
                                                          outputfile=output_file_name)

        df_headers = ['acres',
                      'bmpshortname',
                      'landriversegment',
                      'loadsource',
                      'totalannualizedcostperunit',
                      'totalinstancecost',
                      'bmpfullname',
                      'original_load_N',
                      'original_load_P',
                      'original_load_S',
                      'new_load_N',
                      'new_load_P',
                      'new_load_S',
                      'feasible',
                      'solution_objective',
                      'percent_reduction_minimum'
                      ]

        if not feasible:
            # Create empty dataframes
            merged_df = pd.DataFrame([[None] * len(df_headers)], columns=df_headers)
            merged_df['feasible'] = feasible

            cast_formatted_df = None
            if translate_to_cast_format:
                cast_formatted_df = pd.DataFrame()
        else:
            # Populate dataframe with solution info
            merged_df = initial_solution_parse_to_dataframe(get_suffixes, solved_instance)

            # Add BMP full name
            merged_df['bmpfullname'] = self.jeeves.bmp.fullnames_from_shortnames(merged_df)

            # Add Nutrient Load information
            merged_df['original_load_N'] = pyo.value(solved_instance.original_load_expr['N'])
            merged_df['original_load_P'] = pyo.value(solved_instance.original_load_expr['P'])
            merged_df['original_load_S'] = pyo.value(solved_instance.original_load_expr['S'])
            merged_df['new_load_N'] = pyo.value(solved_instance.new_load_expr['N'])
            merged_df['new_load_P'] = pyo.value(solved_instance.new_load_expr['P'])
            merged_df['new_load_S'] = pyo.value(solved_instance.new_load_expr['S'])

            cast_formatted_df = None
            if translate_to_cast_format:
                # Add state abbreviations to the solution table
                # merged_df = jeeves.bmp.appendBmpType_to_table_with_bmpshortnames(merged_df)

                # Data table generated by separate python script, the set of load source *groups* where each load source *group* contains one and only one load source
                singlelsgrpdf = pd.read_csv(os.path.join(get_raw_data_dir(), 'single-ls_groups.csv'))
                cast_formatted_df = singlelsgrpdf.loc[:, ['loadsourceshortname',
                                                          'loadsourcegroup']].merge(merged_df,
                                                                                    how='inner',
                                                                                    left_on='loadsourceshortname',
                                                                                    right_on='loadsource')

                # Add state abbreviations to the solution table
                lrsegids = self.jeeves.geo.lrseg.ids_from_names(cast_formatted_df['landriversegment'])
                cast_formatted_df['StateAbbreviation'] = self.jeeves.geo.statenames_from_lrsegids(lrsegids)

                # Rename Columns
                cast_formatted_df = cast_formatted_df.rename(index=str, columns={"landriversegment": "GeographyName"})
                cast_formatted_df = cast_formatted_df.rename(index=str, columns={"loadsourcegroup": "LoadSourceGroup"})
                cast_formatted_df = cast_formatted_df.rename(index=str, columns={"bmpshortname": "BmpShortname"})
                cast_formatted_df = cast_formatted_df.rename(index=str, columns={"acres": "Amount"})

                # Add Columns
                cast_formatted_df['AgencyCode'] = 'nonfed'
                cast_formatted_df['Unit'] = 'acres'
                cast_formatted_df['StateUniqueIdentifier'] = 'none'

                # Retain only the necessary columns
                cast_formatted_df = cast_formatted_df.loc[:,
                                    ['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation',
                                     'BmpShortname', 'GeographyName', 'LoadSourceGroup',
                                     'Amount', 'Unit']]

        solution_dict = {'output_file_name': output_file_name,
                         'solution_df': merged_df,
                         'cast_formatted_df': cast_formatted_df,
                         'timestamp': solvetimestamp,
                         'feasible': feasible,
                         'solved_results': solved_results,
                         'model_object': mdl}

        return solution_dict


def solve(localsolver, solvername, instance,
          logfilename='logfile_loadobjective.log',
          get_suffixes=True, solver_options=None, outputfile=None):
    # Wall time - clock starts.
    starttime_modelsolve = time.time()

    if localsolver:
        solver = SolverFactory(solvername)

        # Configure with solver options
        # file_print_levels (Output Level-of-Detail):
        #   4 for just # of iterations, and final objective, infeas,etc. values
        #   6 for summary information about all iterations, but not variable values
        #   8 for variable values at all iterations
        #   10 for all iterations
        if solver_options:
            for k, v in solver_options.items():
                solver.options[k] = v
        solver.options['OF_mumps_mem_percent'] = '5'  # "OF_" prefix signals to Pyomo to create a temporary options file
        solver.options['OF_output_file'] = outputfile

        if get_suffixes:
            instance.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
            instance.ipopt_zL_out = pyo.Suffix(direction=pyo.Suffix.IMPORT)
            instance.ipopt_zU_out = pyo.Suffix(direction=pyo.Suffix.IMPORT)
            setattr(instance, 'lambda', pyo.Suffix(direction=pyo.Suffix.IMPORT))  # use setattr because 'lambda' is reserved keyword

        try:
            results = solver.solve(instance, tee=True, symbolic_solver_labels=True,
                                   keepfiles=False, logfile=logfilename)
        except pyutilib.common._exceptions.ApplicationError:
            traceback.print_exc()
            return None


    else:
        opt = SolverFactory("cbc")
        solver_manager = SolverManagerFactory('neos')

        instance.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
        instance.rc = pyo.Suffix(direction=pyo.Suffix.IMPORT)
        instance.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT_EXPORT)
        # self.instance.slack = pyo.Suffix(direction=pyo.Suffix.IMPORT)

        opt.options["display_width"] = 170
        opt.options["display"] = '_varname, _var.rc, _var.lb, _var, _var.ub, _var.slack'
        results = solver_manager.solve(instance, opt=opt, solver=solvername, logfile=logfilename)

        results.write()

    # Wall time - clock stops.
    _endtime_modelsolve = time.time()
    timefor_modelsolve = _endtime_modelsolve - starttime_modelsolve
    logger.info('*solving done* <- it took %f seconds>' % timefor_modelsolve)

    feasible = check_whether_feasible(instance, results)

    return instance, results, feasible


def check_whether_feasible(model, results):
    """ Check solution feasibility status """
    def check_infeasibility():
        logger.debug('** checking infeasible constraints... **')
        log_infeasible_constraints(model, logger=logger)
        log_infeasible_bounds(model, logger=logger)
    feasible = False
    if (results.solver.status == SolverStatus.ok) and (
            results.solver.termination_condition == TerminationCondition.optimal):
        logger.debug('solution is optimal and feasible')
        feasible = True
    elif results.solver.termination_condition == TerminationCondition.infeasible:
        logger.debug('solution is infeasible')
        check_infeasibility()
    else:
        # Something else is wrong
        logger.debug('Solver Status: %s' % results.solver.status)
        check_infeasibility()
    return feasible


def get_solver_paths(solvername):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    def check_paths_for_solver(name):
        fpath, _ = os.path.split(name)
        solverpath = None
        if fpath:
            if is_exe(name):
                solverpath = name
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, name)
                logger.debug('solver exe file====%s' % exe_file)
                if is_exe(exe_file):
                    solverpath = exe_file
        return solverpath

    solver_path = check_paths_for_solver(solvername)
    if (not solver_path) & (os.name == 'nt'):  # if solver hasn't been found yet, and we're on windows
        solver_path = check_paths_for_solver(solvername + '.exe')

    # If the solver executable is found on PATH, then we check for solver options file in same dir.
    options_file_path = None
    if not not solver_path:
        options_file_path = os.path.join(os.path.dirname(solver_path), 'ipopt.opt')
        try:
            open(options_file_path, 'x')
        except FileExistsError:
            pass  # 'x': exclusive creation - operation fails if file already exists, but creates it if it does not.

        logger.debug('Solver_Path====%s' % options_file_path)

    return solver_path, options_file_path


def solve_problem_instance(modelhandler, mdl, randomstart=False, output_file_str='', fileprintlevel=4):
    """

    Args:
        modelhandler:
        mdl:
        randomstart:
        output_file_str:
        fileprintlevel:

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

    solve_handler = SolveHandler(instance=mdl, localsolver=localsolver, solvername=solvername)

    # ---- Output File Name ----
    if not output_file_str:
        output_file_name = os.path.join(PROJECT_DIR, ''.join(['output/output_', solvetimestamp, '.iters']))
    else:
        output_file_name = os.path.join(PROJECT_DIR, ''.join(['output/output_', output_file_str, '_', solvetimestamp, '.iters']))

    solve_handler.modify_ipopt_options(newoutputfilepath=output_file_name)
    # ---- Output Level-of-Detail ----
    # file_print_levels:
    #   4 for just # of iterations, and final objective, infeas,etc. values
    #   6 for summary information about all iterations, but not variable values
    #   8 for variable values at all iterations
    #   10 for all iterations
    solve_handler.modify_ipopt_options(newfileprintlevel=fileprintlevel)

    # ---- SOLVE ----
    get_suffixes = False
    solved_instance, solved_results, feasible = solve_handler.solve(get_suffixes=get_suffixes)

    # ---- PARSE SOLUTION OUTPUT ----
    # Parse out only the optimal variable values that are nonzero
    # nzvnames, nzvvalues = get_nonzero_var_names_and_values(self.instance)
    solution_handler = SolutionHandler()
    merged_df = solution_handler.get_nonzero_var_df(solved_instance,
                                                    addcosttbldata=modelhandler.datahandler.costsubtbl)
    if get_suffixes:
        # Parse out the Lagrange Multipliers
        lagrange_df = solution_handler.get_lagrangemult_df(solved_instance)
        merged_df = lagrange_df.merge(merged_df,
                                      how='right',
                                      on=['bmpshortname', 'landriversegment', 'loadsource'])

    return output_file_name, merged_df, solvetimestamp, feasible
