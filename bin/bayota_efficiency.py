#!/usr/bin/env python

"""

"""
import timeit
import logging
import argparse
import textwrap

from efficiencysubproblem.src.vis.sequence_plot import plotlib_costobj

from efficiencysubproblem.src.study import Study
from efficiencysubproblem.src.solution_handling.solutionhandler import SolutionHandler

from efficiencysubproblem.config import set_up_logger

# script_dir = os.path.dirname(os.path.realpath(__file__))  # <-- absolute dir of this script
# sys.path.append(script_dir)

set_up_logger()
logger = logging.getLogger(__name__)


def main(numinstances=1, testcase=None, scale='', areanames=None):
    start_time = timeit.default_timer()

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
    parser.add_argument('-t',
                        choices=[1, 2, 3, 99], type=int, help='test case #')
    parser.add_argument('-s', '--scale',
                        action="store", type=str, dest="s",
                        help="geographic scale string", default="")
    parser.add_argument('-a', '--areanames', nargs='+',
                        action="store", type=str, dest="a",
                        help="geographic area names", default="")
    args = parser.parse_args()

    main(testcase=args.t, scale=args.s, areanames=args.a)