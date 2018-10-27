import fileinput
import os
import re
import sys
import time
import logging

import pyomo.environ as oe
from pyomo.opt import SolverFactory, SolverManagerFactory, SolverStatus, TerminationCondition

log = logging.getLogger(__name__)

from bayota_util.infeasible import *


class SolveHandler:
    def __init__(self, instance=None, localsolver=False, solvername=''):

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

    def solve(self, logfilename='logfile_loadobjective.log', get_suffixes=True):
        # Wall time - clock starts.
        starttime_modelsolve = time.time()

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

        # Wall time - clock stops.
        _endtime_modelsolve = time.time()
        timefor_modelsolve = _endtime_modelsolve - starttime_modelsolve
        logger.info('*solving done* <- it took %f seconds>' % timefor_modelsolve)

        # Check solution feasibility status
        def check_infeasibility():
            logger.debug('** checking infeasible constraints... **')
            log_infeasible_constraints(self.instance, logger=logger)
            log_infeasible_bounds(self.instance, logger=logger)
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

        return self.instance, results, feasible
