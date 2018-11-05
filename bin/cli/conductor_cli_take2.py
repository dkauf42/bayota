#!/usr/bin/env python

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

from bayota_settings.install_config import get_graphics_dir, set_up_logger

set_up_logger()
logger = logging.getLogger(__name__)

graphicsdir = get_graphics_dir()


def main(opts):

    start_time = timeit.default_timer()

    s = Study()

    if opts.command == "createmodel":
        print("Createmodel command")
        print("--objective was %s" % opts.objective)
        print("--scale was %s" % opts.scale)
        print("--entities was %s" % opts.entities)

        s = Study(objectivetype=opts.objective,
                  geoscale=opts.scale, geoentities=opts.entities)

    # elif opts.command == "createinstance":
    #     print("Createinstance command")
    #     print("Using %s" % opts.modelfile)
    #     print("--entities was %s" % opts.entities)
    #
    #     s.create_instance(modefile=opts.modelfile, geoentities=opts.entities)

    elif opts.command == "solveinstance":
        print("Solveinstance command")
        print("Using %s" % opts.instancefile)
        print("--constraint was %s" % opts.constraint)

        s.solve_instance(instancefile=opts.instancefile, constraint=opts.constraint)

    else:
        # argparse will error on unexpected commands, but
        # in case we mistype one of the elif statements...
        raise ValueError("Unhandled command %s" % opts.command)

    job_directory = "%s/.job" % os.getcwd()
    scratch = os.environ['SCRATCH']
    data_dir = os.path.join(scratch, '/project/LizardLips')

    # Make top level directories
    os.makedirs(job_directory, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    lizards = ["LizardA", "LizardB"]

    for lizard in lizards:
        job_file = os.path.join(job_directory, "%s.job" % lizard)
        lizard_data = os.path.join(data_dir, lizard)

        # Create lizard directories
        os.makedirs(lizard_data, exist_ok=True)

        with open(job_file) as fh:
            fh.writelines("#!/bin/bash\n")
            fh.writelines("#SBATCH --job-name=%s.job\n" % lizard)
            fh.writelines("#SBATCH --output=.out/%s.out\n" % lizard)
            fh.writelines("#SBATCH --error=.out/%s.err\n" % lizard)
            fh.writelines("#SBATCH --time=2-00:00\n")
            fh.writelines("#SBATCH --mem=12000\n")
            fh.writelines("#SBATCH --qos=normal\n")
            fh.writelines("#SBATCH --mail-type=ALL\n")
            fh.writelines("#SBATCH --mail-user=$USER@stanford.edu\n")
            fh.writelines("Rscript $HOME/project/LizardLips/run.R %s potato shiabato\n" % lizard_data)

        os.system("sbatch %s" % job_file)
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

    # Arguments for top-level, e.g "conductor.py -v"
    parser.add_argument("-v", "--verbose", action="count", default=0)

    subparsers = parser.add_subparsers(dest="command")

    # Make parser for "conductor.py createmodel ..."
    createmodel_parser = subparsers.add_parser("createmodel")
    createmodel_parser.add_argument('-o', '--objective', dest='objective',
                                    choices=['costmin', 'loadreductionmax'], type=str,
                                    help='optimization objective type')
    createmodel_parser.add_argument('-s', '--scale', dest='scale',
                                    choices=['county', 'lrseg'], type=str,
                                    help="geographic scale string")

    # Make parser for "conductor.py createinstance ..."
    createinstance_parser = subparsers.add_parser("createinstance")
    createinstance_parser.add_argument('-m', '--modelfile', dest='modelfile',
                                       type=str,
                                       help="path to pickled abstract model")
    createinstance_parser.add_argument('-e', '--entities', dest='entities',
                                       nargs="*",
                                       help="list of geographic entity names")

    # Make parser for "conductor.py solveinstance ..."
    solveinstance_parser = subparsers.add_parser("solveinstance")
    solveinstance_parser.add_argument('-i', '--instancefile', dest='instancefile',
                                       type=str,
                                       help="path to saved concrete model instance")
    solveinstance_parser.add_argument('-c', '--constraint', dest='constraint',
                                       help="constraint level")

    # Parse
    opts = parser.parse_args()

    # Print option object for debug
    print(opts)

    # args = parser.parse_args()
    # args = parser.parse_args(remaining_argv)
    # print(args)

    main(opts=opts
        )
