import numpy as np
import pandas as pd

tol = 1e-2


def get_nonzero_var_names_and_values(instance):
    # Extract just the nonzero optimal variable values
    nzvarnames = []
    nzvarvalus = []
    for k in instance.x.keys():
        if not not instance.x[k].value:
            if abs(instance.x[k].value) > tol:
                nzvarnames.append(instance.x[k].getname())
                nzvarvalus.append(instance.x[k].value)

    return nzvarnames, nzvarvalus


def get_nonzero_var_df(instance, addcosttbldata=None):
    # Repeat the same thing, but make a DataFrame
    nonzerokeyvals_df = pd.DataFrame([[k, instance.x[k].value]
                                      for k in instance.x.keys()
                                      if (not not instance.x[k].value)
                                      if abs(instance.x[k].value) > tol],
                                     columns=['key', 'value'])

    nonzerodf = pd.DataFrame.from_dict([{'bmpshortname': x[0],
                                         'landriversegment': x[1],
                                         'loadsource': x[2],
                                         'acres': y}
                                        for x, y in zip(nonzerokeyvals_df.key, nonzerokeyvals_df.value)])

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

def get_lagrangemult_df(instance):
    zL_df = pd.DataFrame([[k.index(), instance.ipopt_zL_out[k]]
                          for k in instance.ipopt_zL_out.keys()],
                          columns=['key', 'value'])
    zL_df = pd.DataFrame.from_dict([{'bmpshortname': x[0],
                                     'landriversegment': x[1],
                                     'loadsource': x[2],
                                     'zL': y}
                                    for x, y in zip(zL_df.key, zL_df.value)])
    return zL_df

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
