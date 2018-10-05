import math
import numpy as np
import pandas as pd

tol = 1e-6


class SolutionHandler:
    def __init__(self):
        pass

    @staticmethod
    def get_nonzero_var_names_and_values(instance, onlynotstale=True):
        # Extract just the nonzero optimal variable values
        nzvarnames = []
        nzvarvalus = []
        for k in instance.x.keys():
            if onlynotstale:
                if instance.x[k].stale:
                    continue
            if not not instance.x[k].value:
                if abs(instance.x[k].value) > tol:
                    nzvarnames.append(instance.x[k].getname())
                    nzvarvalus.append(instance.x[k].value)

        return nzvarnames, nzvarvalus

    @staticmethod
    def get_nonzero_var_df(instance, addcosttbldata=None):
        # Repeat the same thing, but make a DataFrame
        nonzerokeyvals_df = pd.DataFrame([[k, instance.x[k].value]
                                          for k in instance.x.keys()
                                          if not instance.x[k].stale
                                          if (not not instance.x[k].value)
                                          if abs(instance.x[k].value) > tol],
                                         columns=['key', 'value'])

        nonzerodf = pd.DataFrame.from_dict([{'bmpshortname': x[0],
                                             'landriversegment': x[1],
                                             'loadsource': x[2],
                                             'acres': y}
                                            for x, y in zip(nonzerokeyvals_df.key, nonzerokeyvals_df.value)])

        if nonzerodf.empty:
            raise ValueError('No non-zero decision variables identified in model instance dataframe')

        if addcosttbldata is not None:
            # add cost/unit data to results table
            costsubtbl = addcosttbldata
            # Retain only those costs pertaining to bmps in our set
            includecols = ['totalannualizedcostperunit', 'bmpshortname']
            nonzerodf = nonzerodf.merge(costsubtbl.loc[:, includecols],
                                        how='left')

            # Add total cost of each BMP to results table for this instance
            nonzerodf['totalinstancecost'] = np.multiply(nonzerodf['totalannualizedcostperunit'].values,
                                                         nonzerodf['acres'].values)

        return nonzerodf

    @staticmethod
    def get_lagrangemult_df(instance):
        # Lower Bounds
        zL_df = pd.DataFrame([[k.index(), instance.ipopt_zL_out[k]]
                              for k in instance.ipopt_zL_out.keys()],
                              columns=['key', 'value'])
        zL_df = pd.DataFrame.from_dict([{'bmpshortname': x[0],
                                         'landriversegment': x[1],
                                         'loadsource': x[2],
                                         'zL': y}
                                        for x, y in zip(zL_df.key, zL_df.value)])

        # Upper Bounds
        zU_df = pd.DataFrame([[k.index(), instance.ipopt_zU_out[k]]
                              for k in instance.ipopt_zU_out.keys()],
                              columns=['key', 'value'])
        zU_df = pd.DataFrame.from_dict([{'bmpshortname': x[0],
                                         'landriversegment': x[1],
                                         'loadsource': x[2],
                                         'zU': y}
                                        for x, y in zip(zU_df.key, zU_df.value)])

        if zU_df.empty:
            out_df = zL_df
        else:
            out_df = zL_df.merge(zU_df,
                                 on=['bmpshortname', 'landriversegment', 'loadsource'])

        return out_df

    @staticmethod
    def get_dual_df(instance):
        # Lower Bounds
        dual_df = pd.DataFrame([[k.index(), instance.dual[k]]
                                for k in instance.dual.keys()],
                               columns=['key', 'value'])
        dual_df.dropna(inplace=True)

        # print(dual_df)
        # [print(instance.BMPS[x[0]]) for x in dual_df.key]

        dual_df = pd.DataFrame.from_dict([{'bmpshortname': instance.BMPS[x[0]],
                                           'landriversegment': x[1],
                                           'loadsource': x[2],
                                           'dual': y}
                                          for x, y in zip(dual_df.key, dual_df.value)])

        # print(dual_df)
        return dual_df

    @staticmethod
    def make_pivot_from_solution_sequence(solution_csv_filepath='', constraint_sequencing_var=''):
        """Load a sequence of solutions with incrementally changing constraint values

        Args:
            solution_csv_filepath (str): full path to csv containing solutions at different constraint values
            constraint_sequencing_var (str): 'tau' or 'totalcostupperbound'

        Returns:
            Pandas.DataFrame: pivoted dataframe, containing one row for each constraint value in the sequence
        """
        df = pd.read_csv(solution_csv_filepath)

        # Pivot table for acres
        df_piv = df.pivot(index=constraint_sequencing_var, columns='x', values='acres')
        df_piv.reset_index(level=[constraint_sequencing_var], inplace=True)  # make tau into a regular column
        df_piv['range'] = df_piv.drop(constraint_sequencing_var,
                                      axis=1).apply(lambda x: list((0, int(math.ceil(np.nanmax(x)) + 1))), 1)
        df_piv['objective'] = df_piv[constraint_sequencing_var].map(dict(zip(df[constraint_sequencing_var],
                                                                             df.solution_objectives)))  # solution_objectives

        return df_piv

# # Other ways to access the optimal values:
# mdl.x['HRTill', 'N51133RL0_6450_0000', 'oac'].value
#
# tol = 1e-6
# for b in mdl.BMPS:
#     for lmbda in mdl.LOADSRCS:
#         bval = mdl.x[b, 'N51133RL0_6450_0000', lmbda].value
#         if not not bval:
#             if abs(bval)>tol:
#                 print('(%s, %s): %d' % (b, lmbda, bval))
