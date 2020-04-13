
# Computation
import numpy as np
import pandas as pd
import pyomo.environ as pyo

# BAYOTA
from bayom_e.model_handling.utils import get_list_of_index_sets
from castjeeves.jeeves import Jeeves

jeeves = Jeeves()


def print_lens(model):
    print(f"# of parcels: {len(model.PARCELS)}")
    print(f"\t# of lrsegs: {len(model.LRSEGS)}")
    print(f"\t# of loadsources: {len(model.LOADSRCS)}")
    print(f"\t# of agencies: {len(model.AGENCIES)}")

    print(f"# of bmps: {len(model.BMPS)}")

    print(f"length of alpha: {len(model.alpha)}")
    print(f"length of eta: {len(model.eta)}")

    print(f"length of Available_Acres_Constraint: {len(model.Available_Acres_Constraint)}")


def print_head(mdl_component, n=5):
    i = 0
    for k, v in mdl_component.items():
        i += 1
        print(f"{k}: {pyo.value(v)}")
        if i > n:
            break

def print_var_head(mdl_var, n=5):
    i = 0
    print(f"key: stale, fixed, lb, value, ub")
    for k, v in mdl_var.items():
        i += 1
        print(f"{k}: {v.stale}, {v.fixed}, {v.lb}, {v.value}, {v.ub}")
        if i > n:
            break

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
    my_component = mdl.original_load_for_each_loadsource_expr

    compsets = get_list_of_index_sets(my_component)

    d = []
    for k, v in my_component.items():
        if k[compsets.index('PLTNTS')] == pltnt:
            d.append({'loadsourceshortname': k[compsets.index('LOADSRCS')],
                      'v': pyo.value(v)})

    df = pd.DataFrame(d).sort_values('loadsourceshortname', ascending=True).reset_index()
    df['loadsource'] = jeeves.loadsource.fullnames_from_shortnames(df['loadsourceshortname'])
    return df

def get_dataframe_of_new_load_for_each_loadsource(mdl, pltnt):
    my_component = mdl.new_load_for_each_loadsource_expr

    compsets = get_list_of_index_sets(my_component)

    d = []
    for k, v in my_component.items():
        if k[compsets.index('PLTNTS')] == pltnt:
            d.append({'loadsourceshortname': k[compsets.index('LOADSRCS')],
                      'v': pyo.value(v)})

    df = pd.DataFrame(d).sort_values('loadsourceshortname', ascending=True).reset_index()
    df['loadsource'] = jeeves.loadsource.fullnames_from_shortnames(df['loadsourceshortname'])
    return df


def get_dataframe_of_original_load_for_each_loadsource_for_a_specific_lrseg(mdl, pltnt, lrsegstr):
    try:
        my_component = mdl.original_load_for_one_parcel_expr
    except AttributeError:
        raise AttributeError("Add 'original_load_for_one_parcel_expr' to the model first!")
    compsets = get_list_of_index_sets(my_component)

    d = []
    for k, v in my_component.items():
        if k[compsets.index('PLTNTS')] == pltnt:
            if k[compsets.index('LRSEGS')] == lrsegstr:
                d.append({'loadsourceshortname': k[compsets.index('LOADSRCS')],
                          'v': pyo.value(v)})

    df = pd.DataFrame(d).sort_values('loadsourceshortname', ascending=True).reset_index()
    df['loadsource'] = jeeves.loadsource.fullnames_from_shortnames(df['loadsourceshortname'],
                                                                   use_order_of_sourcetbl=False)
    return df


def get_dataframe_of_phi_for_each_loadsource_for_a_specific_lrseg(mdl, pltnt, lrsegstr):
    my_component = mdl.phi
    compsets = get_list_of_index_sets(my_component)

    d = []
    for k, v in my_component.items():
        if k[compsets.index('LRSEGS')] == lrsegstr:
            if k[compsets.index('PLTNTS')] == pltnt:
                d.append({'loadsourceshortname': k[compsets.index('LOADSRCS')],
                          'v': pyo.value(v)})

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
    my_component = mdl.alpha
    compsets = get_list_of_index_sets(my_component)

    d = []
    for k, v in my_component.items():
        d.append({'lrseg': k[compsets.index('LRSEGS')],
                  'loadsourceshortname': k[compsets.index('LOADSRCS')],
                  'v': v})

    df = pd.DataFrame(d)
    df = df.groupby('loadsourceshortname').sum().reset_index()
    df['loadsource'] = jeeves.loadsource.fullnames_from_shortnames(df, use_order_of_sourcetbl=False)

    return df