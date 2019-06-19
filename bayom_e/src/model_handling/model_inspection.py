import numpy as np
import pandas as pd

import pyomo.environ as pe

from castjeeves.src.jeeves import Jeeves

jeeves = Jeeves()


def diff_pd(df1, df2):
    """Identify differences between two pandas DataFrames"""
    assert (df1.columns == df2.columns).all(), \
        "DataFrame column names are different"
    if any(df1.dtypes != df2.dtypes):
        "Data Types are different, trying to convert"
        df2 = df2.astype(df1.dtypes)
    if df1.equals(df2):
        return None
    else:
        # need to account for np.nan != np.nan returning True
        diff_mask = (df1 != df2) & ~(df1.isnull() & df2.isnull())
        ne_stacked = diff_mask.stack()
        changed = ne_stacked[ne_stacked]
        changed.index.names = ['id', 'col']
        difference_locations = np.where(diff_mask)
        changed_from = df1.values[difference_locations]
        changed_to = df2.values[difference_locations]
        return pd.DataFrame({'from': changed_from, 'to': changed_to},
                            index=changed.index)


def get_dataframe_of_original_load_for_each_loadsource(mdl, pltnt):
    d = []
    for k, v in mdl.original_load_for_each_loadsource_expr.items():
        if k[0] == pltnt:
            d.append({'loadsourceshortname': k[1],
                      'v': pe.value(v)})

    df = pd.DataFrame(d).sort_values('loadsourceshortname', ascending=True).reset_index()
    df['loadsource'] = jeeves.loadsource.fullnames_from_shortnames(df['loadsourceshortname'],
                                                                   use_order_of_sourcetbl=False)
    return df


def get_dataframe_of_original_load_for_each_loadsource_for_a_specific_lrseg(mdl, pltnt, lrsegstr):
    try:
        mdl.original_load_for_one_parcel_expr
    except AttributeError:
        raise AttributeError("Add 'original_load_for_one_parcel_expr' to the model first!")

    d = []
    for k, v in mdl.original_load_for_one_parcel_expr.items():
        if k[0] == pltnt:
            if k[1] == lrsegstr:
                d.append({'loadsourceshortname': k[2],
                          'v': pe.value(v)})

    df = pd.DataFrame(d).sort_values('loadsourceshortname', ascending=True).reset_index()
    df['loadsource'] = jeeves.loadsource.fullnames_from_shortnames(df['loadsourceshortname'],
                                                                   use_order_of_sourcetbl=False)
    return df


def get_dataframe_of_phi_for_each_loadsource_for_a_specific_lrseg(mdl, pltnt, lrsegstr):
    d = []
    for k, v in mdl.phi.items():
        if k[0] == lrsegstr:
            if k[2] == pltnt:
                d.append({'loadsourceshortname': k[1],
                          'v': pe.value(v)})

    df = pd.DataFrame(d).sort_values('loadsourceshortname', ascending=True).reset_index()
    df['loadsource'] = jeeves.loadsource.fullnames_from_shortnames(df['loadsourceshortname'],
                                                                   use_order_of_sourcetbl=False)
    return df


def get_dataframe_of_T_for_each_loadsource_aggregating_all_lrsegs(mdl):
    """ Total Acres Available for each Load Source

    Args:
        mdl:

    Returns:
        pd.DataFrame

    """
    d = []
    for k, v in mdl.T.items():
        d.append({'lrseg': k[0],
                  'loadsourceshortname': k[1],
                  'v': v})

    df = pd.DataFrame(d)
    df = df.groupby('loadsourceshortname').sum().reset_index()
    df['loadsource'] = jeeves.loadsource.fullnames_from_shortnames(df, use_order_of_sourcetbl=False)

    return df