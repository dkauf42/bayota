#!/usr/bin/env python

"""
Example usage command:
    ./bin/scripts_by_level/run_single_study.py --dryrun -f /Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/bayota/bin/study_specs/single_study_specs/adamsPA_0001.yaml
"""

import os
import subprocess
from argparse import ArgumentParser

from efficiencysubproblem.src import spec_handler


def notdry(dryrun, descr):
    if not dryrun:
        return True
    else:
        print(descr)
        return False


def main(study_model_spec_file, dryrun=False):
    studydict = spec_handler.read(study_model_spec_file)

    EXPERIMENTS = studydict['experiments']
    print('Experiments to be conducted: %s' % EXPERIMENTS)

    '''
    ----------------------------------
    ----------------------------------
    ********** Create Model **********
    ----------------------------------
    ----------------------------------
    '''

    # Create a task to submit to the queue
    CMD = "srun "
    CMD += "study_cli.py generatemodel -f %s " % study_model_spec_file
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

    experiments_dir = studydict['experiments_dir']
    for ii, exp in enumerate(EXPERIMENTS):
        print('Experiment #%d: %s' % (ii+1, exp))

        expdict = spec_handler.read(os.path.join(experiments_dir, exp + '.yaml'))

        TRIALS = expdict['trials']
        print('Trials to be conducted: %s' % TRIALS)

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

    exit(0)  # a clean, no-issue, exit


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()
    one_or_the_other = parser.add_mutually_exclusive_group(required=True)
    one_or_the_other.add_argument("-n", "--study_name", dest="study_name", default=None,
                                  help="name for this study, which should match the study specification file")
    one_or_the_other.add_argument("-f", "--study_model_spec_filepath", dest="study_model_spec_filepath", default=None,
                                  help="path for this study's specification file")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without sending any slurm commands")

    opts = parser.parse_args()

    if not opts.study_model_spec_filepath:  # study name was specified
        opts.study_model_spec_file = os.path.join('study_model_specs', opts.study_name + '.yaml')
    else:  # study filepath was specified
        opts.study_model_spec_file = opts.study_model_spec_filepath

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    main(opts.study_model_spec_file, dryrun=opts.dryrun)
