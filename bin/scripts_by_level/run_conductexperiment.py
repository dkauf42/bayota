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

logger = logging.getLogger('root')
if not logger.hasHandlers():
    set_up_logger()
    logger = logging.getLogger(__name__)

solve_trial_script = os.path.join(get_scripts_dir(), 'run_solveonetrial.py')


def main(experiment_spec_file, saved_model_file=None, dryrun=False):

    expname = os.path.splitext(os.path.basename(experiment_spec_file))[0]

    logger.info('----------------------------------------------')
    logger.info('************* Single Experiment **************')
    logger.info('----------------------------------------------')

    trialnum = 0
    p_list = []
    list_of_trialdicts = read_spec(experiment_spec_file)['trials']
    logger.info(f'\tTrials to be conducted: {list_of_trialdicts}')
    for i, dictwithtrials in enumerate(list_of_trialdicts):
        logger.info(f'trial set #{i}: {dictwithtrials}')

        modvar = dictwithtrials['variable']
        logger.info(f'variable to modify: {modvar}')

        varvalue = dictwithtrials['value']
        logger.info('values: %s' % varvalue)

        varindexer = None
        try:
            varindexer = dictwithtrials['indexer']
            logger.info(f'indexed over: {varindexer}')
        except KeyError:
            pass

        for vi in varvalue:
            trialnum += 1
            trialstr = '{:04}'.format(trialnum)

            logger.info(f'trial #{trialstr}, setting <{modvar}> to <{vi}>')
            modificationstr = f"\'{{\"variable\": \"{modvar}\", " \
                              f"\"value\": {vi}, " \
                              f"\"indexer\": \"{varindexer}\"}}\'"
            # Create a task to submit to the queue
            CMD = "srun "
            CMD += f"{solve_trial_script} " \
                f"-sf {saved_model_file} " \
                f"-tn {expname + '_' + modvar + '_' + trialstr} " \
                f"-m {modificationstr}"
            # Submit the job
            logger.info(f'Job command is: "{CMD}"')
            if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
                p_list.append(subprocess.Popen([CMD], shell=True))

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
