import numpy as np
import pandas as pd

tol = 1e-6


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
        nonzerodf = nonzerodf.merge(costsubtbl.loc[:, includecols])

        # Add total cost of each BMP to results table for this instance
        nonzerodf['totalinstancecost'] = np.multiply(nonzerodf['totalannualizedcostperunit'].values,
                                                     nonzerodf['acres'].values)

    return nonzerodf

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
