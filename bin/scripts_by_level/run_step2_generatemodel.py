#!/usr/bin/env python

"""
Example usage command:

"""
import os
import sys
import time
import logging
from argparse import ArgumentParser

from efficiencysubproblem.src.spec_handler import read_spec, notdry

from efficiencysubproblem.src.model_handling import model_generator
from efficiencysubproblem.src.model_handling.utils import save_model_pickle

from bayota_settings.config_script import set_up_logger, get_model_specs_dir,\
    get_run_specs_dir, get_model_instances_dir

logger = logging.getLogger('root')
if not logger.hasHandlers():
    set_up_logger()
    logger = logging.getLogger(__name__)


geo_spec_file = os.path.join(get_run_specs_dir(), 'geography_specs.yaml')


def main(model_spec_file, geography_name, control_file=None,
         saved_model_file=None, dryrun=False, baseloadingfilename=''):

    logger.info('----------------------------------------------')
    logger.info('************** Model Generation **************')
    logger.info('----------------------------------------------')

    if not not control_file:
        control_dict = read_spec(control_file)
        model_spec_file = control_dict['model']['spec_file']
        geography_scale = control_dict['geography']['scale']
        geography_entity = control_dict['geography']['entity']
        saved_model_file = control_dict['model']['saved_file_for_this_study']
        baseloadingfilename = control_dict['base_loading_file_name']

        logger.info('Geographies specification: %s' % geography_entity)
    else:
        geodict = read_spec(geo_spec_file)[geography_name]
        geography_scale = geodict['scale']
        geography_entity = geodict['entities']
        logger.info('Geographies specification: %s' % geodict)

    if not saved_model_file:
        savepath = os.path.join(get_model_instances_dir(), 'saved_instance.pickle')
    else:
        savepath = saved_model_file

    mdlhandler = None
    if notdry(dryrun, logger, '--Dryrun-- Would generate model'):
        starttime_modelinstantiation = time.time()  # Wall time - clock starts.

        mdlhandler = model_generator.ModelHandlerBase(model_spec_file=model_spec_file,
                                                      geoscale=geography_scale.lower(),
                                                      geoentities=geography_entity,
                                                      savedata2file=False,
                                                      baseloadingfilename=baseloadingfilename)

        timefor_modelinstantiation = time.time() - starttime_modelinstantiation  # Wall time - clock stops.
        logger.info('*model instantiation done* <- it took %f seconds>' % timefor_modelinstantiation)

    save_model_pickle(mdlhandler=mdlhandler, savepath=savepath, dryrun=dryrun)


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()

    # Arguments for top-level
    one_or_the_other = parser.add_mutually_exclusive_group()
    one_or_the_other.add_argument("-n", "--model_spec_name", dest="model_name", default=None,
                                  help="name for this model, which should match the model specification file")
    one_or_the_other.add_argument("-f", "--model_spec_filepath", dest="model_spec_filepath", default=None,
                                  help="path for this model's specification file")
    one_or_the_other.add_argument("-cf", "--control_filepath", dest="control_filepath", default=None,
                                  help="path for this study's control file")

    parser.add_argument("-g", "--geography", dest="geography_name",
                        help="name for a geography defined in geography_specs.yaml")

    one_or_the_other_savemodel = parser.add_mutually_exclusive_group()
    one_or_the_other_savemodel.add_argument("-sn", "--saved_model_name", dest="saved_model_name",
                                            help="name for the saved (pickled) model file")
    one_or_the_other_savemodel.add_argument("-sf", "--saved_model_filepath", dest="saved_model_filepath",
                                            help="path for the saved (pickled) model file")

    parser.add_argument("-bl", "--base_loading", dest="baseloadingfilename",
                        help="name of the base loading file to read from data/raw")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("-v", "--verbose", dest='verbose',
                        action="count", default=0)

    opts = parser.parse_args()

    if not opts.control_filepath:  # control file was not specified
        # MODEL SPEC
        if not opts.model_spec_filepath:  # name was specified
            opts.model_spec_file = os.path.join(get_model_specs_dir(), opts.model_name + '.yaml')
        else:  # filepath was specified
            opts.model_spec_file = opts.model_spec_filepath

        # MODEL SAVE FILE
        if not opts.saved_model_filepath:  # name was specified
            opts.saved_model_file = os.path.join(get_model_instances_dir(), opts.saved_model_name + '.yaml')
        else:  # filepath was specified
            opts.saved_model_file = opts.saved_model_filepath
    else:
        opts.model_spec_file = None
        opts.saved_model_file = None

    print(opts)
    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(opts.model_spec_file, opts.geography_name, control_file=opts.control_filepath,
                  saved_model_file=opts.saved_model_file, dryrun=opts.dryrun,
                  baseloadingfilename=opts.baseloadingfilename))
