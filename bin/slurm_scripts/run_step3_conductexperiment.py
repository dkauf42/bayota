#!/usr/bin/env python
"""
Note: This submits a SLURM "srun" command to launch the 'step4_solveonetrial' script,
      if CLI argument '--no_slurm' is not passed.

Example usage command:
  >> ./bin/slurm_scripts/run_step3_conductexperiment.py --dryrun -cf ~/bayota_ws_0.1a1.dev4/control/step3_experiment_control_b940a328-bf05-4bc0-94e0-bb166eb5880a.yaml
================================================================================
"""
import os
import sys
import datetime
import subprocess
from argparse import ArgumentParser

from bayota_util.spec_and_control_handler import notdry, read_expcon_file, write_control_with_uniqueid

from bayota_settings.base import get_scripts_dir, get_bayota_version
from bayota_settings.log_setup import set_up_detailedfilelogger

logprefix = '** Single Experiment **: '

modify_model_script = os.path.join(get_scripts_dir(), 'run_step3b_modifymodel.py')
solve_trial_script = os.path.join(get_scripts_dir(), 'run_step4_solveonetrial.py')


def main(control_file, dryrun=False, no_slurm=False, log_level='INFO') -> int:
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

    CMD = f"{modify_model_script}  -cn {control_file} --log_level={log_level}"
    if not no_slurm:
        srun_opts = f"--nodes={1} " \
                    f"--ntasks={1} " \
                    f"--cpus-per-task={1} " \
                    f"--exclusive "
        CMD = "srun " + srun_opts + CMD

    # Job is submitted.
    logger.info(f'Job command is: "{CMD}"')
    if notdry(dryrun, logger, '--Dryrun-- Would submit command, then wait.'):
        p1 = subprocess.Popen([CMD], shell=True)
        p1.wait()
        # Get return code from process
        return_code = p1.returncode
        if p1.returncode != 0:
            logger.error(f"Model Modification finished with non-zero code <{return_code}>")
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
            control_dict['code_version']: version
            control_dict['run_timestamps']['step4_trial'] = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            unique_control_name = write_control_with_uniqueid(control_dict=control_dict,
                                                              control_name_prefix='step4_trialcon')

            # A shell command is built for this job submission.
            CMD = f"{solve_trial_script}  -cn {unique_control_name} --log_level={log_level}"
            if not no_slurm:
                srun_opts = f"--nodes={1} " \
                            f"--ntasks={1} " \
                            f"--cpus-per-task={2} " \
                            f"--exclusive "
                CMD = "srun " + srun_opts + CMD

            # Job is submitted.
            logger.info(f'Job command is: "{CMD}"')
            if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
                p_list.append(subprocess.Popen([CMD], shell=True))

    [p.wait() for p in p_list]

    return 0  # a clean, no-issue, exit


def parse_cli_arguments():
    """ Input arguments are parsed. """
    parser = ArgumentParser()
    parser.add_argument("-cn", "--control_filename", dest="control_filename", default=None,
                                  help="name for this study's control file")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("--no_slurm", action='store_true',
                        help="don't use AWS or slurm facilities")

    parser.add_argument("--log_level", nargs=None, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="change logging level to {debug, info, warning, error, critical}")

    opts = parser.parse_args()

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(control_file=opts.control_filename,
                  dryrun=opts.dryrun,
                  no_slurm=opts.no_slurm,
                  log_level=opts.log_level))
