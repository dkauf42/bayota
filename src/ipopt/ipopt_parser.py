import re
import sys
import fileinput
import pandas as pd
from collections import OrderedDict


class IpoptParser:
    """
    Class to hold methods for working with Ipopt output files.

    Specifically designed to be used when running Ipopt from Pyomo.
    """
    def __init__(self):
        pass

    @staticmethod
    def modify_ipopt_options(optionsfilepath='ipopt.opt', newoutputfilepath='', newfileprintlevel=''):
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

        for line in fileinput.FileInput(optionsfilepath, inplace=1):
            parsed = _parse_line(line)
            if parsed:
                if parsed['key'] == 'output_file':
                    if not not newoutputfilepath:
                        line = line.replace(parsed['value'], newoutputfilepath)
                if parsed['key'] == 'file_print_level':
                    if not not newfileprintlevel:
                        line = line.replace(parsed['value'], newfileprintlevel)
            sys.stdout.write(line)

    @staticmethod
    def parse_output_file(filepath):
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

        iterheader_words = ['iter', 'objective', 'inf_pr', 'inf_du', 'lg(mu)',
                            '||d||', 'lg(rg)', 'alpha_du', 'alpha_pr', 'ls']
        rx_iterheader = re.compile(r'''
            iter\s+objective\s+inf_pr\s+inf_du\s+lg\(mu\)\s+\|\|d\|\|\s+lg\(rg\)\s+alpha_du\s+alpha_pr\s+ls
            ''', re.MULTILINE | re.VERBOSE)

        def _parse_headerline(string):
            if rx_iterheader.match(string):
                return True
            return False

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

        iter_summary_data = OrderedDict()
        iter_data_dict = OrderedDict()
        # open the file and read through it line by line
        iternum = None
        with open(output_file_name, 'r') as file_object:
            try:
                while True:
                    line = next(file_object)

                    # Check if it's a new iteration number
                    match = rx_sumiter.search(line)
                    if match:
                        iternum = int(match.group('iterate'))  # set new iterate number
                        if iternum is not None:
                            iter_data_dict[iternum] = []  # reset data list
                            iter_summary_data[iternum] = None

                    if iternum is not None:
                        if _parse_headerline(line):
                            line = next(file_object)
                            parts = line.split()
                            if not not parts:
                                if not parts[-1].isdigit():
                                    iter_summary_data[iternum] = parts[:-1]
                                else:
                                    iter_summary_data[iternum] = parts
                        else:
                            data_line = _parse_line(line)  # at each line check for a match with a regex
                            if data_line:
                                iter_data_dict[iternum].append(data_line)
            except StopIteration:
                pass

        iter_summ_lists = []
        for ii in iter_summary_data.keys():
            iter_summ_lists.append(iter_summary_data[ii])
        print(iter_summ_lists[0])
        summ_df = pd.DataFrame(iter_summ_lists, columns=iterheader_words)

        iter_data_dfs = {}
        for ii in iter_data_dict.keys():
            df = pd.DataFrame(iter_data_dict[ii],
                              columns=['outputname', 'varname', 'componentindex', 'varindex', 'value'])
            df = df.set_index(['componentindex', 'varindex'])
            iter_data_dfs[ii] = df

        return iter_data_dfs, summ_df