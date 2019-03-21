#!/usr/bin/env python

"""
usage: study_cli [<command>] [<args>...] [options]

API for efficiencysubproblem's Study class

Available commands are:
  generatemodel   Parsing args example
  solveinstance  Formatted print example

Example Usage:
    # Just command line arguments:
    > ./bin/study_cli.py generatemodel -o costmin -s county -e "Adams, PA" "Lancaster, PA"
    
    # Just config file argument values
    > ./bin/study_cli.py generatemodel -f adamsPA_costmin.yaml
    
    # With a configuration file and command line arguments:
    > ./bin/study_cli.py generatemodel -f adamsPA_costmin.yaml -s county -e "Adams, PA" "Lancaster, PA"
"""
import os
import sys
import ast
import timeit
import logging
import argparse
import cloudpickle
from configparser import ConfigParser

from efficiencysubproblem.src.study import Study
from efficiencysubproblem.src.solution_handling.solutionhandler import SolutionHandler
from efficiencysubproblem.src.vis.sequence_plot import plotlib_costobj, plotlib_loadreductionobj
from efficiencysubproblem.src import spec_handler

from bayota_settings.base import get_graphics_dir, set_up_logger

set_up_logger()
logger = logging.getLogger(__name__)

graphicsdir = get_graphics_dir()


def main(args):

    objectivetype = args.objective
    scale = args.scale
    entities = args.entities
    baseyear = args.baseyear

    start_time = timeit.default_timer()

    savepath = 'saved_instance.pickle'

    if args.command == 'generatemodel':

        # Create model instance
        s = Study(objectivetype=objectivetype,
                  geoscale=scale, geoentities=entities)

        with open(savepath, "wb") as f:
            cloudpickle.dump(s, f)

    elif args.command == 'solveinstance':

        # A Study instance is read_spec in.
        with open(opts.instancefile, "rb") as f:
            s = cloudpickle.load(f)

        if s.objectivetype == 'costmin':
            constraint_list = list(range(1, 5))
            constraintvar = 'tau'
            plotfunction = plotlib_costobj
        elif s.objectivetype == 'loadreductionmax':
            constraint_list = list(range(100000, 500000, 100000))
            constraintvar = 'tau'
            plotfunction = plotlib_loadreductionobj
        else:
            raise ValueError('unknown objective type')

        # Solve
        (solver_output_filepaths,
         solution_csv_filepath,
         mdf,
         solution_objective,
         feasibility_list) = s.go_constraintsequence(constraint_list)

        df_piv = SolutionHandler.make_pivot_from_solution_sequence(solution_csv_filepath=solution_csv_filepath,
                                                                   constraint_sequencing_var=constraintvar)

        fig = plotfunction(df=df_piv, xname=constraintvar,
                              savefilepathandname=os.path.join(graphicsdir, constraintvar + '_plotlibfig.png'),
                              showplot=False)

    logger.info('<Runner Loading Complete>')
    logger.info("Loading time %s" % (timeit.default_timer() - start_time))
    logger.info('<DONE>')

    return 0


def parse_cli_arguments():
    parser = argparse.ArgumentParser(prog='bayota_efficiency',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     # Turn off help, so we print all options in response to -h
                                     add_help=False)

    # Arguments for top-level
    parser.add_argument("-v", "--verbose", dest='verbose',
                        action="count", default=0)

    parser.add_argument("-f", "--spec_file", dest='conf_file',
                        help="Specification file", metavar="FILE")

    opts, remaining_argv = parser.parse_known_args()

    # Defaults are specified for all of the configuration options.
    studyspec_defaults = {"objective": None,
                          "scale": None,
                          "entities": None,
                          "baseyear": None}
    solveoptions_defaults = {"fileprintlevel": 1}
    instancespec_defaults = {"constraint": 5}
    output_defaults = {'wheretoput': 'hey'}

    # The defaults are merged into one dictionary.
    defaults = dict(studyspec_defaults, **solveoptions_defaults)
    defaults.update(instancespec_defaults)
    defaults.update(output_defaults)

    # Configuration file entries are read_spec to update default values.
    if opts.conf_file:
        studydict = spec_handler.read_spec(opts.conf_file)


        config = ConfigParser()
        config.read([opts.conf_file])

        defaults.update(dict(config.items("StudySpecs")))
        defaults.update(dict(config.items("SolveOptions")))
        defaults.update(dict(config.items("InstanceSpecs")))
        defaults.update(dict(config.items("OutputOptions")))

        defaults['entities'] = ast.literal_eval(defaults['entities'])

    # Parse rest of arguments
    # Don't suppress add_help here so it will handle -h
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        parents=[parser]
    )

    # Make subparsers for "conductor.py generatemodel ..." and "conductor.py solveinstance ..."
    subparsers = parser.add_subparsers(dest="command")
    generatemodel_parser = subparsers.add_parser("generatemodel")
    solveinstance_parser = subparsers.add_parser("solveinstance")
    subparsers.required = True

    generatemodel_parser.set_defaults(**defaults)
    solveinstance_parser.set_defaults(**defaults)

    # The lower-level arguments are defined and added to the appropriate subparsers.
    generatemodel_parser.add_argument('-o', '--objective', dest='objective',
                                       choices=['costmin', 'loadreductionmax'], type=str,
                                       help='optimization objective type')
    generatemodel_parser.add_argument('-s', '--scale', dest='scale',
                                       choices=['county', 'lrseg'], type=str,
                                       help="geographic scale string")
    generatemodel_parser.add_argument('-e', '--entities', dest='entities',
                                       type=str,
                                       nargs="*",
                                       help="list of geographic entity names")
    generatemodel_parser.add_argument('-y', '--baseyear', dest='baseyear',
                                       type=str,
                                       help="base condition (year)")

    solveinstance_parser.add_argument('-i', '--instancefile', dest='instancefile',
                                      type=str,
                                      help="path to saved concrete model instance")
    solveinstance_parser.add_argument('-c', '--constraint', dest='constraint',
                                      help="constraint level")

    # The new arguments are parsed and added to the top-level namespace
    opts = parser.parse_args(remaining_argv, namespace=opts)

    print(opts)
    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # Options in the config file are overwritten by command line arguments.
    if opts.conf_file:
        config = ConfigParser()

        config.read([opts.conf_file])
        config.set("StudySpecs", "objective", opts.objective)
        config.set("StudySpecs", "scale", opts.scale)
        with open(opts.conf_file, "w") as f:
            config.write(f)

    # The main function is called.
    sys.exit(main(opts))
