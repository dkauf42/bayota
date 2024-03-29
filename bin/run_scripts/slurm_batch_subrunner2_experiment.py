#!/usr/bin/env python
""" This submits a SLURM "srun" command to launch the 'step4_solveonetrial' script,

Note: If argument '--no_slurm' is passed, then it will try to run the optimization locally.

Example usage command:
  >> ./bin/run_scripts/slurm_batch_subrunner2_experiment.py --dryrun -cf ~/bayota_ws_0.1a1.dev4/control/step3_experiment_control_b940a328-bf05-4bc0-94e0-bb166eb5880a.yaml
================================================================================
"""

# Generic/Built-in
import os
import sys
import datetime
import subprocess
from argparse import ArgumentParser

# BAYOTA
from bayota_settings.base import get_bayota_version, get_run_steps_dir
from bayota_settings.log_setup import set_up_detailedfilelogger
from bayota_util.spec_and_control_handler import notdry, read_expcon_file, write_control_with_uniqueid

logprefix = '** Single Experiment **: '

modify_model_script = os.path.join(get_run_steps_dir(), 'step2_modifymodel.py')
solve_trial_script = os.path.join(get_run_steps_dir(), 'step3_solveonetrial.py')


def main(control_file, dryrun=False, no_slurm=False, save_to_s3=False, log_level='INFO') -> int:
    version = get_bayota_version()

    # Control file is read.
    control_dict, \
    actionlist, \
    compact_geo_entity_str, \
    expid, \
    expname, \
    list_of_trialdicts, \
    saved_model_file, \
    studyid = read_expcon_file(control_file)

    # Logging formats are set up.
    logger = set_up_detailedfilelogger(loggername=expname,  # same name as module, so logger is shared
                                       filename=f"step3_s{studyid}_e{expid}_{compact_geo_entity_str}.log",
                                       level=log_level,
                                       also_logtoconsole=True,
                                       add_filehandler_if_already_exists=True,
                                       add_consolehandler_if_already_exists=False)

    logger.info('----------------------------------------------')
    logger.info('************* Model Modification *************')
    logger.info('----------------------------------------------')

    # Job command is built and submitted.
    CMD = f"{modify_model_script} {control_file} --log_level={log_level}"
    if save_to_s3:
        CMD = CMD + ' --save_to_s3'
    if not no_slurm:
        slurm_options = f"--nodes={1} " \
                        f"--ntasks={1} " \
                        f"--cpus-per-task={1} " \
                        f"--exclusive "
        CMD = 'srun ' + slurm_options + CMD
    logger.info(f'Job command is: "{CMD}"')
    if notdry(dryrun, logger, '--Dryrun-- Would submit command, then wait.'):
        p = subprocess.Popen([CMD], shell=True)
        p.wait()
        if p.returncode != 0:  # Return code from process is checked.
            logger.error(f"Model Modification finished with non-zero code <{p.returncode}>")
            return 1

    logger.info('----------------------------------------------')
    logger.info('*************** Trials looping ***************')
    logger.info('----------------------------------------------')

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
            trialidstr = '{:04}'.format(trialnum)

            logger.info(f'trial #{trialidstr}, setting <{modvar}> to <{vi}>')
            modificationstr = f"\'{{\"variable\": \"{modvar}\", " \
                              f"\"value\": {vi}, " \
                              f"\"indexer\": \"{varindexer}\"}}\'"

            # A trial control ("trialcon") file is generated by adding to the expcon file.
            control_dict['trial'] = {'id': trialidstr,
                                     'trial_name': 'exp--' + expname + '--_modvar--' + modvar + '--_trial' + trialidstr,
                                     'modification': modificationstr,
                                     'solutions_folder_name': expname}
            control_dict['trial']['uuid'] = control_dict['experiment']['uuid'] + '_t' + trialidstr
            control_dict['code_version']: version
            control_dict['run_timestamps']['step4_trial'] = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            unique_control_name = write_control_with_uniqueid(control_dict=control_dict, name_prefix='step4_trialcon',
                                                              logger=logger)

            # Job command is built and submitted.
            CMD = f"{solve_trial_script} {unique_control_name} --log_level={log_level}"
            if save_to_s3:
                CMD = CMD + ' --save_to_s3'
            if not no_slurm:
                slurm_options = f"--nodes={1} " \
                                f"--ntasks={1} " \
                                f"--cpus-per-task={2} " \
                                f"--exclusive "
                CMD = 'srun ' + slurm_options + CMD
            logger.info(f'Job command is: "{CMD}"')
            if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
                p_list.append(subprocess.Popen([CMD], shell=True))

    [p.wait() for p in p_list]

    return 0  # a clean, no-issue, exit


def parse_cli_arguments():
    """ Input arguments are parsed. """
    parser = ArgumentParser(description="Run an optimization Experiment")

    parser.add_argument("control_filename", metavar='Control Filename', type=str,
                        help="name for this experiment's control file")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("--no_slurm", action='store_true',
                        help="don't use the Slurm job manager")

    parser.add_argument("--save_to_s3", dest="save_to_s3", action='store_true',
                        help="Move model instance and progress files from local workspace to s3 buckets")

    parser.add_argument("--log_level", nargs=None, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="change logging level to {debug, info, warning, error, critical}")

    opts = parser.parse_args()

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(opts.control_filename,
                  dryrun=opts.dryrun,
                  no_slurm=opts.no_slurm,
                  save_to_s3=opts.save_to_s3,
                  log_level=opts.log_level))
