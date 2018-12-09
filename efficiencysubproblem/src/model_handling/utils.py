import pyomo.environ as pe
from itertools import compress

import logging
logger = logging.getLogger('root')


def extract_indexed_expression_values(indexed_expr):
    """Returns the values of an indexed expression (PYOMO object)."""
    return dict((ind, pe.value(val)) for ind, val in indexed_expr.items())  # changed for use with python3, from iteritems()


def modify_model(model, actiondict=None):
    if actiondict['action'] == 'add_component':
        if actiondict['component_type'] == 'Param':
            # logger.info(actiondict['args'])
            # Set the model Object
            setattr(model, actiondict['name'], pe.Param(**actiondict['args']))

        # elif actiondict['component_type'] == 'Constraint':
        #     print(actiondict['args'])
        #     # Set the model Object
        #     setattr(model, actiondict['name'], pe.Constraint(**actiondict['args']))
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
