import math
import os
import pandas as pd

import pyomo.environ as pyo

from bayom_e.data_handling.data_interface import get_dataplate
from bayota_util.spec_handler import read_spec

from bayom_e.model_handling.builders.nonlinear_variant import NonlinearVariant
from bayom_e.model_handling.builders.linear_variant import LinearVariant

from bayota_settings.log_setup import set_up_detailedfilelogger


def check_for_problems_in_data_before_model_construction(data, logger):
    """

    Args:
        data:
        logger:

    Returns:

    """
    for key in data.tau:
        if data.tau[key] < 0:
            msg = f"*warning* the bmp '{key}' has a negative unit cost ({data.tau[key]})!"
            if logger:
                logger.warn(msg)
            else:
                print(msg)


def check_for_problems_post_model_construction(model, logger):
    """

    Args:
        model:
        logger:

    Returns:

    """

    def original_loadsource_problems_dataframe(mdl):
        d = []
        for k, v in mdl.original_load_for_each_loadsource_expr.items():
            if math.isinf(pyo.value(v)) | math.isnan(pyo.value(v)):
                d.append({'pollutant': k[0],
                          'loadsourceshortname': k[1],
                          'v': pyo.value(v)})

        df = pd.DataFrame(d)
        if df.empty:
            pass  # Good, no Inf's or NaN's
        else:
            df = df.sort_values('loadsourceshortname', ascending=True).reset_index()
        return df

    original_load_error = False
    # Check for Inf or NaN original loads
    for p in model.PLTNTS:
        if math.isinf(pyo.value(model.original_load_expr[p])):
            logger.error(f"Uh oh! original_load_expr for {p} is Inf")
            original_load_error = True
        elif math.isnan(pyo.value(model.original_load_expr[p])):
            logger.error(f"Uh oh! original_load_expr for {p} is NaN")
            original_load_error = True

    if original_load_error:
        logger.debug(original_loadsource_problems_dataframe(model).head())


def build_model(model_spec_file, geoscale, geoentities, baseloadingfilename,
                savedata2file=False, log_level='INFO'):
    """Generate a model for the efficiency BMPs.

    Args:
        model_spec_file (str): path to a model specification file
        geoscale (str):
        geoentities (list):
        baseloadingfilename (str):
        savedata2file (bool):
        log_level (:obj:`str`, optional): The log-level for the model generation logger. Defaults to 'INFO'.

    Returns
        a Pyomo ConcreteModel

    """
    logger = set_up_detailedfilelogger(loggername=os.path.splitext(os.path.basename(model_spec_file))[0],
                                       filename='bayota_model_generation.log',
                                       level=log_level,
                                       also_logtoconsole=True,
                                       add_filehandler_if_already_exists=False,
                                       add_consolehandler_if_already_exists=False)

    """ Initialization; Get Data """
    # parse_model_spec(specdict=read_spec(model_spec_file))
    specdict = read_spec(model_spec_file)
    dataplate = get_dataplate(geoscale=geoscale, geoentities=[geoentities],
                              savedata2file=savedata2file, baseloadingfilename=baseloadingfilename)
    check_for_problems_in_data_before_model_construction(data=dataplate, logger=logger)

    """ Build the model skeleton (sets, parameters, and variables) """
    variant = specdict['variant']
    if variant == 'nlp':
        builder = NonlinearVariant(logger=logger)
    elif variant == 'lp':
        builder = LinearVariant(logger=logger)
    else:
        raise ValueError(f"unrecognized model variant <{variant}>")
    print(specdict.items())
    model = builder.build_model(dataplate, geoscale=geoscale, specdict=specdict)

    """ The model is validated. """
    check_for_problems_post_model_construction(model, logger)

    return model, dataplate