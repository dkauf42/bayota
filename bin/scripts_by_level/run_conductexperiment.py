#!/usr/bin/env python

"""
Example usage command:

"""
import os
import sys
import time
import logging
import subprocess
from argparse import ArgumentParser
import cloudpickle

from efficiencysubproblem.src.spec_handler import read_spec, notdry
from efficiencysubproblem.src.solver_handling import solvehandler

from bayota_settings.config_script import set_up_logger, get_experiment_specs_dir,\
    get_scripts_dir, get_model_instances_dir
# set_up_logger()
# logger = logging.getLogger(__name__)
# logger = logging.getLogger('root')

logger = logging.getLogger('root')
if not logger.hasHandlers():
    set_up_logger()
    logger = logging.getLogger(__name__)

solve_trial_script = os.path.join(get_scripts_dir(), 'run_solveonetrial.py')


def main(experiment_spec_file, saved_model_file=None, dryrun=False):

    logger.info('----------------------------------------------')
    logger.info('************* Single Experiment **************')
    logger.info('----------------------------------------------')

    # TRIALS = read_spec(experiment_spec_file)['trials']
    # logger.info('\tTrials to be conducted: %s' % TRIALS)
    # for trial in TRIALS:
    #     # Create a task to submit to the queue
    #     CMD = "srun "
    #     CMD += "%s -n %s -sf %s" % (experiment_script, expspec_file, saved_model_file_for_this_study)
    #     # Submit the job
    #     logger.info('Job command is: "%s"' % CMD)
    #     if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
    #         p_list.append(subprocess.Popen([CMD], shell=True))

    p_list = []
    list_of_trialdicts = read_spec(experiment_spec_file)['trials']
    logger.info('\tTrials to be conducted: %s' % list_of_trialdicts)
    for i, dictwithtrials in enumerate(list_of_trialdicts):
        logger.info('trial set #%d: %s' % (i, dictwithtrials))
        for k, v in dictwithtrials.items():
            logger.info('variable to modify: %s' % k)
            logger.info('values: %s' % v)
            for j, vi in enumerate(v):
                logger.info('trial #%d, setting <%s> to <%s>' % (j, k, vi))
                modificationstr = "{'variable': '%s', 'value': %s}" % (k, vi)
                # Create a task to submit to the queue
                CMD = "srun "
                CMD += "%s -sf %s -m %s" % (solve_trial_script, saved_model_file, modificationstr)
                # Submit the job
                logger.info('Job command is: "%s"' % CMD)
                if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
                    p_list.append(subprocess.Popen([CMD], shell=True))

                break
        break

    [p.wait() for p in p_list]


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()

    # Arguments for top-level
    one_or_the_other = parser.add_mutually_exclusive_group()
    one_or_the_other.add_argument("-n", "--experiment_spec_name", dest="experiment_name", default=None,
                                  help="name for this experiment, which should match the experiment specification file")
    one_or_the_other.add_argument("-f", "--experiment_spec_filepath", dest="experiment_spec_filepath", default=None,
                                  help="path for this experiment's specification file")

    one_or_the_other_savemodel = parser.add_mutually_exclusive_group()
    one_or_the_other_savemodel.add_argument("-sn", "--saved_model_name", dest="saved_model_name",
                                            help="name for the saved (pickled) model file")
    one_or_the_other_savemodel.add_argument("-sf", "--saved_model_filepath", dest="saved_model_filepath",
                                            help="path for the saved (pickled) model file")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without sending any slurm commands")

    parser.add_argument("-v", "--verbose", dest='verbose',
                        action="count", default=0)

    opts = parser.parse_args()

    # EXPERIMENT SPEC
    if not opts.experiment_spec_filepath:  # name was specified
        opts.experiment_spec_file = os.path.join(get_experiment_specs_dir(), opts.experiment_name + '.yaml')
    else:  # filepath was specified
        opts.experiment_spec_file = opts.experiment_spec_filepath

    # MODEL SAVE FILE
    if not opts.saved_model_filepath:  # name was specified
        opts.saved_model_file = os.path.join(get_model_instances_dir(), opts.saved_model_name + '.yaml')
    else:  # filepath was specified
        opts.saved_model_file = opts.saved_model_filepath

    print(opts)
    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(opts.experiment_spec_file, saved_model_file=opts.saved_model_file, dryrun=opts.dryrun))
