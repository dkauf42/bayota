#!/usr/bin/env python

"""
Example usage command:
    ./bin/scripts_by_level/run_single_study.py --dryrun -f /Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/bayota/bin/study_specs/single_study_specs/adamsPA_0001.yaml
"""

import os
import sys
import logging
import subprocess
from argparse import ArgumentParser

from efficiencysubproblem.src import spec_handler

from bayota_settings.config_script import get_output_dir, \
    set_up_logger, get_bayota_version, get_run_specs_dir, get_experiment_specs_dir
set_up_logger()
logger = logging.getLogger(__name__)
outdir = get_output_dir()


def notdry(dryrun, descr):
    if not dryrun:
        return True
    else:
        logger.info(descr)
        return False


def main(study_spec_file, dryrun=False):
    studydict = spec_handler.read_spec(study_spec_file)

    version = get_bayota_version()
    logger.info('----------------------------------------------')
    logger.info('*********** BayOTA version %s *************' % version)
    logger.info('----------------------------------------------')
    logger.info('************** Single Study RUN **************')
    logger.info('----------------------------------------------')

    EXPERIMENTS = studydict['experiments']
    logger.info('Experiments in study spec: %s' % EXPERIMENTS)

    '''
    ----------------------------------
    ----------------------------------
    ********** Create Model **********
    ----------------------------------
    ----------------------------------
    '''

    # Create a task to submit to the queue
    CMD = "srun "
    CMD += "study_cli.py generatemodel -f %s " % study_spec_file
    CMD += "&"
    # Submit the job
    if notdry(dryrun, '--Dryrun-- Would submit job command: <%s>' % CMD):
        subprocess.call([CMD], shell=True)

    if notdry(dryrun, '--Dryrun-- Would wait'):
        subprocess.call(["wait"], shell=True)

    '''
    ----------------------------------
    ----------------------------------
    **** Loop through experiments ****
    ******* and conduct trials *******
    ----------------------------------
    ----------------------------------
    '''

    experiments_dir = get_experiment_specs_dir()
    for ii, exp in enumerate(EXPERIMENTS):
        logger.info('Exp. #%d: %s' % (ii+1, exp))

        expdict = spec_handler.read_spec(os.path.join(experiments_dir, exp + '.yaml'))

        TRIALS = expdict['trials']
        logger.info('\tTrials to be conducted: %s' % TRIALS)

        for trial in TRIALS:
            # Create a task to submit to the queue
            CMD = "srun "
            CMD += "study_cli.py solveinstance --instancefile %s " % opts.study_name
            CMD += "&"
            # Submit the job
            if notdry(dryrun, '--Dryrun-- Would submit job command: <%s>' % CMD):
                subprocess.call([CMD], shell=True)

    if notdry(dryrun, '--Dryrun-- Would wait'):
        subprocess.call(["wait"], shell=True)

    return 0  # a clean, no-issue, exit


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()
    one_or_the_other = parser.add_mutually_exclusive_group(required=True)
    one_or_the_other.add_argument("-n", "--study_name", dest="study_name", default=None,
                                  help="name for this study, which should match the study specification file")
    one_or_the_other.add_argument("-f", "--study_spec_filepath", dest="study_spec_filepath", default=None,
                                  help="path for this study's specification file")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without sending any slurm commands")

    opts = parser.parse_args()

    if not opts.study_spec_filepath:  # study name was specified
        opts.study_spec_file = os.path.join(get_run_specs_dir(), 'single_study_specs', opts.study_name + '.yaml')
    else:  # study filepath was specified
        opts.study_spec_file = opts.study_spec_filepath

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    sys.exit(main(opts.study_spec_file, dryrun=opts.dryrun))
