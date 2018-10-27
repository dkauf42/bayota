#!/usr/bin/env python

"""
Example Usage:
    # Just command line arguments:
    >>> ./bin/study_cli.py -o costmin -s county -e "Adams, PA" "Lancaster, PA"
    
    # Just config file argument values
    >>> ./bin/study_cli.py @study_config.cfg
    
    # With a configuration file and command line arguments:
    #   Note: config file (with @ symbol) must come before cli arguments,
    #         if you want cli args to take precedence over config file values
    >>> ./bin/study_cli.py @study_config.cfg -s county -e "Adams, PA" "Lancaster, PA"
"""
import os
import ast
import timeit
import logging
import argparse
import textwrap
from configparser import ConfigParser

from efficiencysubproblem.src.study import Study
from efficiencysubproblem.src.solution_handling.solutionhandler import SolutionHandler
from efficiencysubproblem.src.vis.sequence_plot import plotlib_costobj

from bayota_settings.logging import set_up_logger
from bayota_settings.output_paths import get_graphics_dir

set_up_logger()
logger = logging.getLogger(__name__)

graphicsdir = get_graphics_dir()


def main(objectivetype, scale, entities, baseyear):

    start_time = timeit.default_timer()

    s = Study(objectivetype=objectivetype,
              geoscale=scale, geoentities=entities)

    # countyname = g.split(',')[0]
    # stateabbrev = g.split(',')[1]

    (solver_output_filepaths,
     solution_csv_filepath,
     mdf,
     solution_objective,
     feasibility_list) = s.go_constraintsequence(list(range(1, 5)))

    constraintvar = 'tau'
    df_piv = SolutionHandler.make_pivot_from_solution_sequence(solution_csv_filepath=solution_csv_filepath,
                                                               constraint_sequencing_var=constraintvar)

    fig = plotlib_costobj(df=df_piv, xname=constraintvar,
                          savefilepathandname=os.path.join(graphicsdir,'tau1-10' + '_plotlibfig.png'),
                          secondaryxticklabels=df_piv['N_pounds_reduced'],
                          showplot=False)

    logger.info('<Runner Loading Complete>')
    logger.info("Loading time %s" % (timeit.default_timer() - start_time))
    logger.info('<DONE>')

    return None


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='bayota_efficiency',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''\
                                                 Create and run an optimization case
                                                 --------------------------------
                                                 1. Generate a Decision Space    
                                                      * specify metadata
                                                         - base condition
                                                         - wastewatername data
                                                         - cost profile
                                                         - geography
                                                      * specify free parameter groups
                                                      * specify constraints
                                                 2. Generate a Scenario
                                                 '''),
                                     # Turn off help, so we print all options in response to -h
                                     add_help=False)

    parser.add_argument("-c", "--conf_file",
                        help="Specify config file", metavar="FILE")
    args, remaining_argv = parser.parse_known_args()

    defaults = {"objective":None,
                "scale": None,
                "entities": None,
                "baseyear": None}

    if args.conf_file:
        config = ConfigParser()
        config.read([args.conf_file])
        defaults.update(dict(config.items("Defaults")))

    print(defaults)
    defaults['entities'] = ast.literal_eval(defaults['entities'])
    print(defaults)

    # Parse rest of arguments
    # Don't suppress add_help here so it will handle -h
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        parents=[parser]
    )
    parser.set_defaults(**defaults)
    parser.add_argument('-o', '--objective', dest='objective',
                        choices=['costmin', 'loadreductionmax'], type=str,
                        help='optimization objective type')

    parser.add_argument('-s', '--scale', dest='scale',
                        choices=['county', 'lrseg'], type=str,
                        help="geographic scale string")

    parser.add_argument('-e', '--entities', dest='entities',
                        type=str,
                        nargs="*",
                        help="list of geographic entity names")

    parser.add_argument('-y', '--baseyear', dest='baseyear',
                        type=str,
                        nargs="*",
                        help="base condition (year)")

    # args = parser.parse_args()
    args = parser.parse_args(remaining_argv)
    print(args)
    main(objectivetype=args.objective,
         scale=args.scale,
         entities=args.entities,
         baseyear=args.baseyear,

         )
