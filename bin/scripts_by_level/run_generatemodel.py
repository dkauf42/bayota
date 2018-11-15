#!/usr/bin/env python

"""
Example usage command:

"""
import os
import sys
import ast
import timeit
import logging
import argparse
from argparse import ArgumentParser
import cloudpickle
from configparser import ConfigParser

from efficiencysubproblem.src.study import Study
from efficiencysubproblem.src.model_handling.utils import parse_model_spec
from efficiencysubproblem.src.model_handling.interface import get_loaded_model_handler
from efficiencysubproblem.src.solution_handling.solutionhandler import SolutionHandler
from efficiencysubproblem.src.vis.sequence_plot import plotlib_costobj, plotlib_loadreductionobj
from efficiencysubproblem.src import spec_handler

from bayota_settings.config_script import get_graphics_dir, set_up_logger

set_up_logger()
logger = logging.getLogger(__name__)

graphicsdir = get_graphics_dir()

start_time = timeit.default_timer()

savepath = 'saved_instance.pickle'


def main(model_spec_file, dryrun=False):
    print(parse_model_spec(model_spec_file))
    exit(0)

    Study().makemodel_from_file(modelspecfile=model_spec_file)
    # OR

    # A modelhandler object is instantiated, generating the model and setting instance data.
    modelhandler = get_loaded_model_handler(objectivetype, geoscale, geoentities, savedata2file=False)
    
    # Create model instance
    s = Study(objectivetype=opts.objectivetype,
              geoscale=opts.scale, geoentities=opts.entities)

    with open(savepath, "wb") as f:
        cloudpickle.dump(s, f)


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()

    # Arguments for top-level
    one_or_the_other = parser.add_mutually_exclusive_group()
    one_or_the_other.add_argument("-n", "--model_spec_name", dest="model_name", default=None,
                                  help="name for this model, which should match the model specification file")
    one_or_the_other.add_argument("-f", "--model_spec_filepath", dest="model_spec_filepath", default=None,
                                  help="path for this model's specification file")

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
        opts.model_spec_file = os.path.join('study_model_specs', opts.model_name + '.yaml')
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
    sys.exit(main(opts.model_spec_file, dryrun=opts.dryrun))