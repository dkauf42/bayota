#!/usr/bin/env python
"""
Note: This submits a SLURM "srun" command to launch the 'step2_generatemodel' script,
      if CLI argument '--no_slurm' is not passed.

Example usage command:
  >> ./bin/run_scripts/slurm_batch_subrunner1_study.py --dryrun -cf ~/bayota_ws_0.1a1.dev4/control/step1_study_control_1ccccab7-dfbe-4974-86ed-5744b659f938.yaml
================================================================================
"""
import os
import sys
import subprocess
from argparse import ArgumentParser

from bayota_settings.base import get_output_dir, get_slurm_scripts_dir, get_run_steps_dir
from bayota_settings.log_setup import set_up_detailedfilelogger
from bayota_util.spec_and_control_handler import read_spec, notdry, read_study_control_file, write_control_with_uniqueid

outdir = get_output_dir()

model_generator_script = os.path.join(get_run_steps_dir(), 'step1_generatemodel.py')
experiment_script = os.path.join(get_slurm_scripts_dir(), 'slurm_batch_subrunner2_experiment.py')


def main(control_file, dryrun=False, no_slurm=False, save_to_s3=False, log_level='INFO') -> int:
    # Load and save new control file
    control_dict, \
    experiments, \
    baseloadingfilename, \
    geography_name, \
    compact_geo_entity_str, \
    model_spec_name, \
    studyshortname, \
    studyid = read_study_control_file(control_file)

    # Logging formats are set up.
    logger = set_up_detailedfilelogger(loggername=studyshortname,  # same name as module, so logger is shared
                                       filename=f"step1_s{studyid}_{compact_geo_entity_str}.log",
                                       level=log_level,
                                       also_logtoconsole=True,
                                       add_filehandler_if_already_exists=True,
                                       add_consolehandler_if_already_exists=False)

    logger.info('----------------------------------------------')
    logger.info('******* %s *******' % ('BayOTA').center(30, ' '))
    logger.info('*************** Single Study *****************')
    logger.info('----------------------------------------------')
    logger.info(f"Geography = {geography_name}")
    logger.info(f"Model specification name = {model_spec_name}")
    logger.info(f"Experiments = {experiments}")
    logger.info(f"Base_loading_file_name = {baseloadingfilename}")
    logger.info('')
    logger.info('----------------------------------------------')
    logger.info('************** Model Generation **************')
    logger.info('----------------------------------------------')

    # Job command is built and submitted.
    CMD = f"{model_generator_script} {control_file} --log_level={log_level}"
    if save_to_s3:
        CMD = CMD + ' --save_to_s3'
    if not no_slurm:
        slurm_options = f"--nodes={1} " \
                        f"--ntasks={1} " \
                        f"--exclusive "
        CMD = 'srun ' + slurm_options + CMD
    logger.info(f'Job command is: "{CMD}"')
    if notdry(dryrun, logger, '--Dryrun-- Would submit command, then wait.'):
        p = subprocess.Popen([CMD], shell=True)
        p.wait()
        if p.returncode != 0:    # Return code from process is checked.
            logger.error(f"Model Generator finished with non-zero code <{p.returncode}>")
            return 1

    # A job is submitted for each experiment in the list.
    p_list = []
    for ii, exp_spec_name in enumerate(experiments):
        expid = '{:04}'.format(ii+1)
        logger.info(f"Exp. #{expid}: {exp_spec_name}")

        expactiondict = read_spec(spec_file_name=exp_spec_name, spectype='experiment')

        # An experiment control ("expcon") file is generated by adding to the studycon file.
        try:
            del control_dict["experiments"]
        except KeyError:
            logger.info("Key 'experiments' not found")
        control_dict['experiment_name'] = exp_spec_name
        expactiondict['id'] = expid
        control_dict['experiment'] = expactiondict
        control_dict['experiment']['uuid'] = control_dict['study']['uuid'] + '_e' + expid
        unique_control_name = write_control_with_uniqueid(control_dict=control_dict, name_prefix='step3_expcon',
                                                          logger=logger)

        # Job command is built and submitted.
        CMD = f"{experiment_script} {unique_control_name} --log_level={log_level}"
        if save_to_s3:
            CMD = CMD + ' --save_to_s3'
        if no_slurm:
            CMD = CMD + " --no_slurm"
        logger.info(f'Job command is: "{CMD}"')
        if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
            p_list.append(subprocess.Popen([CMD], shell=True))

    if notdry(dryrun, logger, '--Dryrun-- Would wait'):
        [p.wait() for p in p_list]

    return 0  # a clean, no-issue, exit


def parse_cli_arguments():
    """ Input arguments are parsed. """
    parser = ArgumentParser(description="Run an optimization Study")

    parser.add_argument("control_filename", metavar='Control Filename', type=str,
                        help="name for this study's control file")

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

    sys.exit(main(opts.control_filename,
                  dryrun=opts.dryrun,
                  no_slurm=opts.no_slurm,
                  save_to_s3=opts.save_to_s3,
                  log_level=opts.log_level))
