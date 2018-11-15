#!/usr/bin/env python

"""
Example usage command:
    ./bin/scripts_by_level/run_batch_of_studies.py --dryrun -f /Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/bayota/bin/study_specs/batch_study_specs/maryland_counties.yaml
"""

import os
import sys
import subprocess
from argparse import ArgumentParser

from efficiencysubproblem.src import spec_handler


def notdry(dryrun, descr):
    if not dryrun:
        return True
    else:
        print(descr)
        return False


def main(batch_spec_file, dryrun=False):
    batchdict = spec_handler.read_spec(batch_spec_file)

    STUDIES = batchdict['studies']
    print('Studies to be conducted: %s' % STUDIES)

    NUMNODES = 1
    PRIORITY = 5000
    SLURM_OUTPUT = 'slurm_out'

    for study in STUDIES:
        # Create a job to submit to the HPC with sbatch
        CMD = "sbatch "
        CMD += "--job-name=%s " % study
        CMD += "--nice=%s " % PRIORITY
        CMD += "--nodes=%s " % NUMNODES # nodes requested
        CMD += "--output=%s " % SLURM_OUTPUT
        CMD += "--time=01:00:00 "  # time requested in hour:minute:second
        CMD += "run_single_study.py -n %s " % study

        # Submit the job
        if notdry(dryrun, '--Dryrun- Would submit job command: <%s>' % CMD):
            subprocess.call([CMD], shell=True)

    return 0  # a clean, no-issue, exit


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()
    one_or_the_other = parser.add_mutually_exclusive_group(required=True)
    one_or_the_other.add_argument("-n", "--batch_spec_name", dest="batch_name", default=None,
                                  help="name for this batch, which should match the batch specification file")
    one_or_the_other.add_argument("-f", "--batch_spec_filepath", dest="batch_spec_filepath", default=None,
                                  help="path for this batch's specification file")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without sending any slurm commands")

    opts = parser.parse_args()

    if not opts.batch_spec_filepath:  # name was specified
        opts.batch_spec_file = os.path.join('study_model_specs', opts.batch_name + '.yaml')
    else:  # filepath was specified
        opts.batch_spec_file = opts.batch_spec_filepath

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    sys.exit(main(opts.batch_spec_file, dryrun=opts.dryrun))
