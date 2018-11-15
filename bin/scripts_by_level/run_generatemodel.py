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
    get_run_specs_dir, get_source_pickles_dir
# set_up_logger()
# logger = logging.getLogger(__name__)
# logger = logging.getLogger('root')

logger = logging.getLogger('root')
if not logger.hasHandlers():
    set_up_logger()
    logger = logging.getLogger(__name__)


savepath = os.path.join(get_source_pickles_dir(), 'saved_instance.pickle')
geo_spec_file = os.path.join(get_run_specs_dir(), 'geography_specs.yaml')


def main(model_spec_file, geography_name, dryrun=False):
    geodict = read_spec(geo_spec_file)[geography_name]

    logger.info('----------------------------------------------')
    logger.info('************** Model Generation **************')
    logger.info('----------------------------------------------')

    logger.info('Geographies specification: %s' % geodict)

    if notdry(dryrun, logger, '--Dryrun-- Would generate model'):
        starttime_modelinstantiation = time.time()  # Wall time - clock starts.

        mdl = model_generator.ModelHandlerBase(model_spec_file=model_spec_file,
                                               geoscale=geodict['scale'],
                                               geoentities=geodict['entities'],
                                               savedata2file=False)

        timefor_modelinstantiation = time.time() - starttime_modelinstantiation  # Wall time - clock stops.
        logger.info('*model instantiation done* <- it took %f seconds>' % timefor_modelinstantiation)

    if notdry(dryrun, logger, '--Dryrun-- Would save model as pickle with name <%s>' % savepath):
        starttime_modelsave = time.time()  # Wall time - clock starts.
        with open(savepath, "wb") as f:
            cloudpickle.dump(mdl, f)
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

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without sending any slurm commands")

    parser.add_argument("-v", "--verbose", dest='verbose',
                        action="count", default=0)

    opts = parser.parse_args()

    # opts, remaining_argv = parser.parse_known_args()
    #
    # # Defaults are given for all of the model specifications.
    # studyspec_defaults = {"objective": None,
    #                       "scale": None,
    #                       "entities": None,
    #                       "baseyear": None}
    # solveoptions_defaults = {"fileprintlevel": 1}
    # instancespec_defaults = {"constraint": 5}
    # output_defaults = {'wheretoput': 'hey'}
    #
    # # The defaults are merged into one dictionary.
    # defaults = dict(studyspec_defaults, **solveoptions_defaults)
    # defaults.update(instancespec_defaults)
    # defaults.update(output_defaults)
    #
    # # Configuration file entries are read_spec to update default values.
    # if opts.model_spec_filepath:
    #     studydict = spec_handler.read_spec(opts.model_spec_filepath)
    #
    #     config = ConfigParser()
    #     config.read_spec([opts.model_spec_filepath])
    #
    #     defaults.update(dict(config.items("StudySpecs")))
    #     defaults.update(dict(config.items("SolveOptions")))
    #     defaults.update(dict(config.items("InstanceSpecs")))
    #     defaults.update(dict(config.items("OutputOptions")))
    #
    #     defaults['entities'] = ast.literal_eval(defaults['entities'])
    #
    # # Parse rest of arguments
    # # Don't suppress add_help here so it will handle -h
    # # parser = argparse.ArgumentParser(
    # #     # Inherit options from config_parser
    # #     parents=[parser]
    # # )
    #
    # parser.set_defaults(**defaults)
    #
    # cli_model_spec_group = parser.add_argument_group()
    # # The lower-level arguments are defined and added to the appropriate subparsers.
    # cli_model_spec_group.add_argument('-o', '--objective', dest='objective',
    #                                   choices=['costmin', 'loadreductionmax'], type=str,
    #                                   help='optimization objective type')
    # cli_model_spec_group.add_argument('-s', '--scale', dest='scale',
    #                                   choices=['county', 'lrseg'], type=str,
    #                                   help="geographic scale string")
    # cli_model_spec_group.add_argument('-e', '--entities', dest='entities',
    #                                   type=str,
    #                                   nargs="*",
    #                                   help="list of geographic entity names")
    # cli_model_spec_group.add_argument('-y', '--baseyear', dest='baseyear',
    #                                   type=str,
    #                                   help="base condition (year)")
    #
    # # The new arguments are parsed and added to the top-level namespace
    # opts = parser.parse_args(remaining_argv, namespace=opts)
    #
    if not opts.model_spec_filepath:  # name was specified
        opts.model_spec_file = os.path.join(get_model_specs_dir(), opts.model_name + '.yaml')
    else:  # filepath was specified
        opts.model_spec_file = opts.model_spec_filepath

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
    sys.exit(main(opts.model_spec_file, opts.geography_name, dryrun=opts.dryrun))
