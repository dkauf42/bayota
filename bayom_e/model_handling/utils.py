""" Helpful methods used when handling pyomo models
"""

# Generic/Built-in
import time
import logging
from itertools import compress

# Computation
import cloudpickle
import numpy as np
import pyomo.environ as pyo

# BAYOTA
from bayota_util.spec_and_control_handler import notdry

logger = logging.getLogger('root')


class model_as_func_for_pygmo:
    """ For use with PYGMO black-box optimization package"""
    def __init__(self, dim, pyomo_model=None,
                 objective1_name=None, objective1_indexer=None, objective1_sign=1,
                 objective2_name=None, objective2_indexer=None, objective2_sign=1):
        self.dim = dim
        self.model = pyomo_model

        self.objective1_name = objective1_name
        self.objective1_indexer = objective1_indexer
        self.objective1_sign = objective1_sign

        self.objective2_name = objective2_name
        self.objective2_indexer = objective2_indexer
        self.objective2_sign = objective2_sign

    def fitness(self, x):
        """ Define objectives """
        # Values for the model variables are set.
        varcomponent = self.model.x
        for k, d in zip(varcomponent.items(), x):
            varcomponent[k[0]] = d

        # Objective value is evaluated.
        obj1_att = getattr(self.model, self.objective1_name)
        if self.objective2_indexer:
            f1 = self.objective1_sign * pyo.value(obj1_att[self.objective1_indexer])
        else:
            f1 = self.objective1_sign * pyo.value(obj1_att)

        obj2_att = getattr(self.model, self.objective2_name)
        if self.objective2_indexer:
            f2 = self.objective2_sign * pyo.value(obj2_att[self.objective2_indexer])
        else:
            f2 = self.objective2_sign * pyo.value(obj2_att)

        return [f1, f2]

    def get_nobj(self):
        """ Return number of objectives """
        return 2

    def get_name(self):
        return "cast optimization function"

    def get_bounds(self):
        """ Return bounds of decision variables """
        upper = list()
        lower = list()
        for k, v in self.model.x.items():
            upper.append(v.ub)
            lower.append(v.lb)

        return np.array(lower), np.array(upper)


def extract_indexed_expression_values(indexed_expr):
    """Returns the values of an indexed expression (PYOMO object)."""
    return dict((ind, pyo.value(val)) for ind, val in indexed_expr.items())  # changed for use with python3, from iteritems()


def get_list_of_index_sets(mdl_component):
    return [s.name for s in mdl_component._implicit_subsets]

def modify_model(model, actiondict=None):
    if actiondict['action'] == 'add_component':
        if actiondict['component_type'] == 'Param':
            # logger.info(actiondict['args'])
            # Set the model Object
            setattr(model, actiondict['name'], pyo.Param(**actiondict['args']))

        # elif actiondict['component_type'] == 'Constraint':
        #     print(actiondict['args'])
        #     # Set the model Object
        #     setattr(model, actiondict['name'], pyo.Constraint(**actiondict['args']))
    elif actiondict['action'] == 'fix_variable':
        idxset = actiondict['index']['set']
        idxval = actiondict['index']['value']
        fix_value = actiondict['value']

        # find which element in the index tuple do we need to compare
        compbool = [idxset == st._name for st in model.x._index.set_tuple]

        ii = 0
        for idxtuple in model.component('x'):
            compval = list(compress(idxtuple, compbool))[0]
            if compval.lower() == idxval.lower():
                ii += 1
                model.x[idxtuple].fix(fix_value)

        # Check whether any values were found
        if ii == 0:
            logger.info('model_handling.util.modify_model(): '
                        'No Matching values found')
        else:
            logger.info('model_handling.util.modify_model(): '
                        '%d values matching the index <%s> were fixed to %d' %
                        (ii, idxval, fix_value))


def save_model_pickle(model, savepath, dryrun=False, logprefix=''):
    # Save the model handler object
    if notdry(dryrun, logger, '--Dryrun-- Would save model as pickle with name <%s>' % savepath):
        starttime_modelsave = time.time()  # Wall time - clock starts.
        with open(savepath, "wb") as f:
            cloudpickle.dump(model, f)
        timefor_modelsave = time.time() - starttime_modelsave  # Wall time - clock stops.
        logger.info(f"*{logprefix} - model pickling done* <- it took {timefor_modelsave} seconds>")


def load_model_pickle(savepath, dryrun=False, logprefix='') -> pyo.ConcreteModel:
    model = None
    if notdry(dryrun, logger, '--Dryrun-- Would load model from pickle with name <%s>' % savepath):
        starttime_modelload = time.time()  # Wall time - clock starts.
        with open(savepath, "rb") as f:
            model = cloudpickle.load(f)
        timefor_modelload = time.time() - starttime_modelload  # Wall time - clock stops.
        logger.info(
            f"*{logprefix} - model load (from pickle) done* <- it took {timefor_modelload} seconds>")
    return model
