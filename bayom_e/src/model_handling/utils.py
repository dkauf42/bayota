import time
import cloudpickle
import pyomo.environ as pe
from itertools import compress

from bayota_util.spec_handler import notdry
from bayom_e.src.model_handling.model_generator import ModelHandlerBase

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


def save_model_pickle(mdlhandler, savepath, dryrun=False, logprefix=''):
    # Save the model handler object
    if notdry(dryrun, logger, '--Dryrun-- Would save model as pickle with name <%s>' % savepath):
        starttime_modelsave = time.time()  # Wall time - clock starts.
        with open(savepath, "wb") as f:
            cloudpickle.dump(mdlhandler, f)
        timefor_modelsave = time.time() - starttime_modelsave  # Wall time - clock stops.
        logger.info(f"*{logprefix} - model pickling done* <- it took {timefor_modelsave} seconds>")


def load_model_pickle(savepath, dryrun=False, logprefix='') -> ModelHandlerBase:
    mdlhandler = None
    if notdry(dryrun, logger, '--Dryrun-- Would load model from pickle with name <%s>' % savepath):
        starttime_modelload = time.time()  # Wall time - clock starts.
        with open(savepath, "rb") as f:
            mdlhandler = cloudpickle.load(f)
        timefor_modelload = time.time() - starttime_modelload  # Wall time - clock stops.
        logger.info(
            f"*{logprefix} - model load (from pickle) done* <- it took {timefor_modelload} seconds>")
    return mdlhandler
