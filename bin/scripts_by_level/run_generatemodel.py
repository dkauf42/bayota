#!/usr/bin/env python

"""
Example usage command:

"""
import os
import sys
import time
import logging
from argparse import ArgumentParser
import cloudpickle

from efficiencysubproblem.src.spec_handler import read_spec, notdry

from efficiencysubproblem.src.model_handling import model_generator

from bayota_settings.config_script import set_up_logger, get_model_specs_dir,\
    get_run_specs_dir, get_model_instances_dir

logger = logging.getLogger('root')
if not logger.hasHandlers():
    set_up_logger()
    logger = logging.getLogger(__name__)


geo_spec_file = os.path.join(get_run_specs_dir(), 'geography_specs.yaml')


def main(model_spec_file, geography_name, saved_model_file=None, dryrun=False):
    geodict = read_spec(geo_spec_file)[geography_name]

    if not saved_model_file:
        savepath = os.path.join(get_model_instances_dir(), 'saved_instance.pickle')
    else:
        savepath = saved_model_file

    logger.info('----------------------------------------------')
    logger.info('************** Model Generation **************')
    logger.info('----------------------------------------------')

    logger.info('Geographies specification: %s' % geodict)

    mdlhandler = None
    if notdry(dryrun, logger, '--Dryrun-- Would generate model'):
        starttime_modelinstantiation = time.time()  # Wall time - clock starts.

        mdlhandler = model_generator.ModelHandlerBase(model_spec_file=model_spec_file,
                                                      geoscale=geodict['scale'],
                                                      geoentities=geodict['entities'],
                                                      savedata2file=False)

        timefor_modelinstantiation = time.time() - starttime_modelinstantiation  # Wall time - clock stops.
        logger.info('*model instantiation done* <- it took %f seconds>' % timefor_modelinstantiation)

    if notdry(dryrun, logger, '--Dryrun-- Would save model as pickle with name <%s>' % savepath):
        starttime_modelsave = time.time()  # Wall time - clock starts.
        with open(savepath, "wb") as f:
            cloudpickle.dump(mdlhandler, f)
        timefor_modelsave = time.time() - starttime_modelsave  # Wall time - clock stops.
        logger.info('*model pickling done* <- it took %f seconds>' % timefor_modelsave)


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()

    # Arguments for top-level
    one_or_the_other = parser.add_mutually_exclusive_group()
    one_or_the_other.add_argument("-n", "--model_spec_name", dest="model_name", default=None,
                                  help="name for this model, which should match the model specification file")
    one_or_the_other.add_argument("-f", "--model_spec_filepath", dest="model_spec_filepath", default=None,
                                  help="path for this model's specification file")

    parser.add_argument("-g", "--geography", dest="geography_name",
                        help="name for a geography defined in geography_specs.yaml")

    one_or_the_other_savemodel = parser.add_mutually_exclusive_group()
    one_or_the_other_savemodel.add_argument("-sn", "--saved_model_name", dest="saved_model_name",
                                            help="name for the saved (pickled) model file")
    one_or_the_other_savemodel.add_argument("-sf", "--saved_model_filepath", dest="saved_model_filepath",
                                            help="path for the saved (pickled) model file")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without sending any slurm commands")

    parser.add_argument("-v", "--verbose", dest='verbose',
                        action="count", default=0)

    opts = parser.parse_args()

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

    print(opts)
    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # # Options in the config file are overwritten by command line arguments.
    # if opts.model_spec_filepath:
    #     config = ConfigParser()
    #
    #     config.read_spec([opts.model_spec_filepath])
    #     config.set("StudySpecs", "objective", opts.objective)
    #     config.set("StudySpecs", "scale", opts.scale)
    #     with open(opts.model_spec_filepath, "w") as f:
    #         config.write(f)

    # The main function is called.
    sys.exit(main(opts.model_spec_file, opts.geography_name, saved_model_file=opts.saved_model_file, dryrun=opts.dryrun))
