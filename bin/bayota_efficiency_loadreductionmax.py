#!/usr/bin/env python

"""
Example Usage:
    >>> ./bin/bayota_efficiency_loadreductionmax.py -s county -e "Adams, PA" "Lancaster, PA"
"""
import os
import timeit
import logging
import argparse
import textwrap

from efficiencysubproblem.src.vis.sequence_plot import plotlib_loadreductionobj

from efficiencysubproblem.src.study import Study
from efficiencysubproblem.src.solution_handling.solutionhandler import SolutionHandler

from bayota_settings.logging import set_up_logger

from bayota_settings.output_paths import get_graphics_dir
graphicsdir = get_graphics_dir()

# script_dir = os.path.dirname(os.path.realpath(__file__))  # <-- absolute dir of this script
# sys.path.append(script_dir)

set_up_logger()
logger = logging.getLogger(__name__)


def main(objectivetype, scale, entities):
    start_time = timeit.default_timer()

    listofgeos = entities
    if not entities:
        listofgeos = ['Allegany, MD',
                      'Anne Arundel, MD',
                      'Baltimore City, MD',
                      'Calvert, MD',
                      'Caroline, MD',
                      'Carroll, MD',
                      'Cecil, MD',
                      'Charles, MD',
                      'Dorchester, MD',
                      'Frederick, MD',
                      'Garrett, MD',
                      'Harford, MD',
                      'Howard, MD',
                      'Kent, MD',
                      'Montgomery, MD',
                      'Prince Georges, MD',
                      'Queen Annes, MD',
                      'St. Marys, MD',
                      'Baltimore, MD']

    for g in listofgeos:
        print(g)
        s = Study(objectivetype=objectivetype,
                  geoscale=scale, geoentities=[g])

        countyname = g.split(',')[0]
        stateabbrev = g.split(',')[1]

        (solver_output_filepaths,
         solution_csv_filepath,
         mdf,
         solution_objective,
         feasibility_list) = s.go_constraintsequence(list(range(0, 1000000, 100000)))

        constraintvar = 'totalcostupperbound'
        df_piv = SolutionHandler.make_pivot_from_solution_sequence(solution_csv_filepath=solution_csv_filepath,
                                                                   constraint_sequencing_var=constraintvar)

        fig = plotlib_loadreductionobj(df=df_piv, xname=constraintvar,
                              savefilepathandname=os.path.join(graphicsdir,
                                                               stateabbrev + countyname + '_totalcostbound1-1mil' + '_plotlibfig.png'),
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
                                                 '''))
    parser.add_argument('-o', '--objective', dest='o',
                        choices=['costmin', 'loadreductionmax'], type=str,
                        help='optimization objective type',
                        default='loadreductionmax')

    parser.add_argument('-s', '--scale', dest='s',
                        choices=['county', 'lrseg'], type=str,
                        help="geographic scale string",
                        default="county")

    parser.add_argument('-e', '--entities', dest='e',
                        type=str,
                        nargs="*",
                        help="list of geographic entity names",
                        default="")

    args = parser.parse_args()

    main(objectivetype=args.o, scale=args.s, entities=args.e)