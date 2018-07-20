import re
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
        lagrange_df = get_lagrangemult_df(self.instance)
        # Parse out only the optimal variable values that are nonzero
        nzvnames, nzvvalues = get_nonzero_var_names_and_values(self.instance)
        nonzerodf = get_nonzero_var_df(self.instance, addcosttbldata=self.data.costsubtbl)
        merged_df = lagrange_df.merge(nonzerodf,
                                      how='right',
                                      on=['bmpshortname', 'landriversegment', 'loadsource'])

        return merged_df

    def parse_output_file(self, filepath):
        """
        Parse text at given filepath

        Parameters
        ----------
        filepath : str
            Filepath for file_object to be parsed

        Returns
        -------
        data : pd.DataFrame
            Parsed data

        """
        # output_file_name = 'ipopt_output_file'  # defined in the ipopt.opt file
        # output_file_name = 'test_ipopt_output_file.txt'
        output_file_name = filepath

        rx_vars = re.compile(r'''
            ^
            (?P<outputname>[a-zA-Z0-9_ ]*)
            (?P<componentindex>\[[0-9 ]+\]){
            (?P<varname>\w*)
            (?P<varindex>\[\w+[\w,]+\])\}=
            (?P<value>[\s-]?(?:0|[1-9]\d*)(?:\.\d*)?(?:[eE][+\-]?\d+)?)
        ''', re.MULTILINE | re.VERBOSE)

        rx_sumiter = re.compile(r'''
            ^
            (?:\*+\s+Summary\sof\sIteration:\s)
            (?P<iterate>\d+):
        ''', re.MULTILINE | re.VERBOSE)

        def _parse_line(string):
            """
            Do a regex search against all defined regexes and
            return the key and match result of the first matching regex

            """
            iterator = rx_vars.finditer(string)

            row = []
            for match in iterator:
                if match:
                    row = {'outputname': match.group('outputname'),
                           'varname': match.group('varname'),
                           'componentindex': match.group('componentindex'),
                           'varindex': match.group('varindex'),
                           'value': match.group('value')
                           }

                elif match == '':
                    print('empty string')
                    return None
                else:
                    print('No match')
                    return None

            return row

        iter_data_dict = {}
        # open the file and read through it line by line
        iternum = None
        with open(output_file_name, 'r') as file_object:
            #     for lines in range(500000):
            # #         i+=1
            #         line = file_object.readline()
            for line in file_object:
                # Check if it's a new iteration number
                match = rx_sumiter.search(line)
                if match:
                    iternum = int(match.group('iterate'))  # set new iterate number
                    if iternum is not None:
                        iter_data_dict[iternum] = []  # reset data list

                if iternum is not None:
                    data_line = _parse_line(line)  # at each line check for a match with a regex
                    if data_line:
                        iter_data_dict[iternum].append(data_line)

        iter_data_dfs = {}
        for ii in iter_data_dict.keys():
            df = pd.DataFrame(iter_data_dict[ii],
                              columns=['outputname', 'varname', 'componentindex', 'varindex', 'value'])
            df = df.set_index(['componentindex', 'varindex'])
            iter_data_dfs[ii] = df
            # print('iterate #: %s' % ii)
            # print(df.head(5))

        return iter_data_dfs
