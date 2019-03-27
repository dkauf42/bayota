#!/usr/bin/env python
"""
Note: This submits a SLURM "srun" command to launch the 'step4_solveonetrial' script,
      if CLI argument '--no_slurm' is not passed.

Example usage command:
  >> ./bin/run_scripts/run_step3_conductexperiment.py --dryrun -cf ~/bayota_ws_0.1a1.dev4/control/step3_experiment_control_b940a328-bf05-4bc0-94e0-bb166eb5880a.yaml
================================================================================
"""
import os
import sys
import uuid
import yaml
import datetime
import subprocess
from argparse import ArgumentParser

from efficiencysubproblem.src.spec_handler import read_spec, notdry
from efficiencysubproblem.src.model_handling.utils import modify_model, save_model_pickle, load_model_pickle

from bayota_settings.base import get_experiment_specs_dir,\
    get_scripts_dir, get_model_instances_dir, get_control_dir, get_bayota_version
from bayota_settings.log_setup import root_logger_setup

logprefix = '** Single Experiment **: '

solve_trial_script = os.path.join(get_scripts_dir(), 'run_step4_solveonetrial.py')


def main(experiment_spec_file, saved_model_file=None, control_file=None,
         dryrun=False, no_slurm=False, log_level='INFO') -> int:
    logger = root_logger_setup(consolehandlerlevel=log_level, filehandlerlevel='DEBUG')

    version = get_bayota_version()
    logger.info('----------------------------------------------')
    logger.info('************ Experiment Launching ************')
    logger.info('----------------------------------------------')

    # The control file is read.
    if not not control_file:
        control_dict = read_spec(control_file)

        expname = os.path.splitext(os.path.basename(control_dict['experiment_file']))[0]
        saved_model_file = control_dict['model']['saved_file_for_this_study']
        actionlist = control_dict['experiment']['exp_setup']
        list_of_trialdicts = control_dict['experiment']['trials']
    else:
        control_dict = dict()
        expname = os.path.splitext(os.path.basename(experiment_spec_file))[0]
        actionlist = read_spec(experiment_spec_file)['exp_setup']
        list_of_trialdicts = read_spec(experiment_spec_file)['trials']

    # The model is modified according to specified experiment set-up
    logger.info(f"{logprefix} {expname} - modification action list = {actionlist}")
    if notdry(dryrun, logger, '--Dryrun-- Would modify model with action <%s>' % actionlist):

        # Check whether any model modifications are specified
        if actionlist[0] == 'none':
            logger.info(f"{logprefix} {expname} - no model modifications made")
        else:
            # Load the model object
            mdlhandler = load_model_pickle(savepath=saved_model_file, dryrun=dryrun)

            for a in actionlist:
                modify_model(mdlhandler.model, actiondict=a)

            save_model_pickle(mdlhandler=mdlhandler, savepath=saved_model_file, dryrun=dryrun, logprefix=logprefix)

    # List of trial sets to be conducted for this experiment are logged.
    tempstr = 'set' if len(list_of_trialdicts) == 1 else 'sets'
    logger.info(f"{logprefix} {expname} - trial {tempstr} to be conducted: {list_of_trialdicts}")

    # Loop through and start each trial
    trialnum = 0
    p_list = []
    for i, dictwithtrials in enumerate(list_of_trialdicts):
        logger.info(f'{logprefix} {expname} - trial set #{i}: {dictwithtrials}')

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

            # Generate a trial control file with a unique identifier (uuid4), by adding onto the experiment control file
            unique_control_file = os.path.join(get_control_dir(), 'step4_trial_control_' + str(uuid.uuid4()) + '.yaml')
            control_dict['trial'] = {'str': trialstr,
                                     'trial_name': 'experiment--' + expname + '--_modifiedvar--' + modvar + '--_trial' + trialstr,
                                     'modification': modificationstr,
                                     'solutions_folder_name': expname}
            control_dict['code_version']: version
            control_dict['run_timestamps']['step4_trial'] = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')

            with open(unique_control_file, "w") as f:
                yaml.safe_dump(control_dict, f, default_flow_style=False)

            # A shell command is built for this job submission.
            CMD = f"{solve_trial_script}  -cf {unique_control_file} --log_level={log_level}"
            if not no_slurm:
                srun_opts = f"--nodes={1} " \
                            f"--ntasks={1} " \
                            f"--exclusive "
                CMD = "srun " + srun_opts + CMD

            # Job is submitted.
            logger.info(f'Job command is: "{CMD}"')
            if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
                p_list.append(subprocess.Popen([CMD], shell=True))

    [p.wait() for p in p_list]

    return 0  # a clean, no-issue, exit


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()

    # Arguments for top-level
    one_or_the_other = parser.add_mutually_exclusive_group()
    one_or_the_other.add_argument("-n", "--experiment_spec_name", dest="experiment_name", default=None,
                                  help="name for this experiment, which should match the experiment specification file")
    one_or_the_other.add_argument("-f", "--experiment_spec_filepath", dest="experiment_spec_filepath", default=None,
                                  help="path for this experiment's specification file")
    one_or_the_other.add_argument("-cf", "--control_filepath", dest="control_filepath", default=None,
                                  help="path for this study's control file")

    one_or_the_other_savemodel = parser.add_mutually_exclusive_group()
    one_or_the_other_savemodel.add_argument("-sn", "--saved_model_name", dest="saved_model_name",
                                            help="name for the saved (pickled) model file")
    one_or_the_other_savemodel.add_argument("-sf", "--saved_model_filepath", dest="saved_model_filepath",
                                            help="path for the saved (pickled) model file")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("--no_slurm", action='store_true',
                        help="don't use AWS or slurm facilities")

    parser.add_argument("--log_level", nargs=None, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="change logging level to {debug, info, warning, error, critical}")

    opts = parser.parse_args()

    if not not opts.control_filepath:  # a control file was specified
        pass
    else:
        # EXPERIMENT SPEC
        if not opts.experiment_spec_filepath:  # name was specified instead
            opts.experiment_spec_filepath = os.path.join(get_experiment_specs_dir(), opts.experiment_name + '.yaml')
        # MODEL SAVE FILE
        if not opts.saved_model_filepath:  # name was specified instead
            opts.saved_model_filepath = os.path.join(get_model_instances_dir(), opts.saved_model_name + '.yaml')

    print(opts)
    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(opts.experiment_spec_filepath,
                  saved_model_file=opts.saved_model_filepath,
                  control_file=opts.control_filepath,
                  dryrun=opts.dryrun,
                  no_slurm=opts.no_slurm,
                  log_level=opts.log_level))
