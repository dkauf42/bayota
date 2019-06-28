from pyomo.opt import SolverFactory
import pyomo.environ as pyo
import pandas as pd
import os
import re


def gjh_solve(instance, keepfiles=True, amplenv=None, basegjhpath=''):
    opt2 = SolverFactory('gjh')
    solved_instance, solved_results = opt2.solve(instance, keepfiles=keepfiles)

    # Get the output file name
    str1 = solved_instance.Solver._list[0].Message
    # matches = re.findall('\w+\.pyomo\.gjh', str1)

    rx = re.compile('\s*\"(?P<filepath>(?:[^\"])*)\"\s*written', re.MULTILINE)
    match = rx.search(str1)
    if match:
        fpath = match.group('filepath')
        print(fpath)
    else:
        fpath = None
        print('NO MATCH')

    # print(all_same(matches))
    gjh_filename = fpath
    print(basegjhpath)
    print(gjh_filename)

    r2dat = amplenv.read(os.path.join(basegjhpath, gjh_filename))
    g = amplenv.getParameter('g')
    # g_df = g.getValues().toPandas()

    return gjh_filename, g


def make_df(instance=None, filterbydf=None, g=None):
    dict_for_df = {}

    for v in instance.component_objects(pyo.Var, active=True):
        print("Variable component object", v)
        i = 0
        for index in v:
            if not filterbydf.empty:
                if filterbydf['bmpshortname'].str.contains(index[0]).any() & \
                   filterbydf['landriversegment'].str.contains(index[1]).any() & \
                   filterbydf['loadsource'].str.contains(index[2]).any():
                    try:
                        x_value = pyo.value(v[index])
                        i += 1
                        try:
                            # print (i,"   ", index, v[index].value, g[i])
                            dict_for_df[index] = g[i]  # store in a dict
                        except:
                            pass
                    except:
                        pass
            else:
                try:
                    x_value = pyo.value(v[index])
                    i += 1
                    try:
                        # print (i,"   ", index, v[index].value, g[i])
                        dict_for_df[index] = g[i]  # store in a dict
                    except:
                        pass
                except:
                    pass

    g_df = pd.DataFrame.from_dict([{'bmpshortname': x[0],
                                    'landriversegment': x[1],
                                    'loadsource': x[2],
                                    'g': y}
                                   for x, y in zip(dict_for_df.keys(), dict_for_df.values())])
    return g_df


def all_same(items):
    return all([x == items[0] for x in items])


