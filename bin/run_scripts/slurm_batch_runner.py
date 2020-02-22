#!/usr/bin/env python
"""
Note: This submits a SLURM "sbatch" command to launch the 'step1_single_study' script,
      if CLI argument '--no_slurm' is not passed.

Example usage command:
  >> ./bin/run_scripts/slurm_batch_runner.py --dryrun -n maryland_counties
================================================================================
"""
import os
import sys
import datetime
import subprocess
from argparse import ArgumentParser

from bayota_settings.base import get_bayota_version, get_slurm_scripts_dir
from bayota_settings.log_setup import root_logger_setup
from bayota_util.spec_and_control_handler import notdry, parse_batch_spec, write_control_with_uniqueid

single_study_script = os.path.join(get_slurm_scripts_dir(), 'slurm_batch_subrunner1_study.py')


def main(batch_spec_name, dryrun=False, no_slurm=False, save_to_s3=False, log_level='INFO') -> int:
    # Logging formats are set up.
    logger = root_logger_setup(consolehandlerlevel=log_level, filehandlerlevel='DEBUG')
    logger.debug(locals())

    version = get_bayota_version()
    logger.info('----------------------------------------------')
    logger.info('******* %s *******' % ('BayOTA version ' + version).center(30, ' '))
    logger.info('************** Batch of studies **************')
    logger.info('----------------------------------------------')

    # Specification file is read.
    geo_scale, study_pairs, control_options = parse_batch_spec(batch_spec_name, logger=logger)

    # Study pairs (Geography, Model+Experiments) are looped through (and submitted as SLURM "sbatch" jobs).
    for index, sp in enumerate(study_pairs):
        studyid = '{:04}'.format(index+1)
        geoname = sp[0]
        filesafegeostring = geoname.replace(' ', '').replace(',', '')
        studyspecdict = sp[1]
        spname = filesafegeostring + f"_s{studyid}"
        studyspecdict['studyshortname'] = spname
        studyspecdict['id'] = studyid

        # A study control ("studycon") file with a unique identifier (uuid4) is created.
        control_dict = {"geography": {'scale': geo_scale, 'entity': geoname},
                        "study": studyspecdict, "control_options": control_options,
                        "code_version": version,
                        "run_timestamps": {'step0_batch': datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}}
        unique_control_name = write_control_with_uniqueid(control_dict=control_dict, name_prefix='step1_studycon',
                                                          logger=logger)

        # Job command is built and submitted.
        #     Each Node has 36 cpus.  We want to use 32 of them.  Each task ("trial") will be able to use 2 cpus.
        CMD = f"{single_study_script} {unique_control_name} --log_level={log_level}"
        if save_to_s3:
            CMD = CMD + ' --save_to_s3'
        if not no_slurm:
            slurm_options = f"--job-name={spname} " \
                            f"--nice={5000} " \
                            f"--cpus-per-task={2} " \
                            f"--nodes={1} " \
                            f"--ntasks={16} " \
                            f"--output=slurm_job_{spname}_%j-%2t.out " \
                            f"--error=slurm_job_{spname}_%j-%2t.err " \
                            f"--time=12:00:00 "  # time requested in hour:minute:second
            CMD = 'sbatch ' + slurm_options + CMD
        else:
            CMD = CMD + " --no_slurm"
        logger.info(f'Job command is: "{CMD}"')
        if notdry(dryrun, logger, '--Dryrun- Would submit command'):
            subprocess.Popen([CMD], shell=True)

    return 0  # a clean, no-issue, exit


def parse_cli_arguments():
    """ Input arguments are parsed. """
    parser = ArgumentParser(description="Run a batch of optimization studies")

    parser.add_argument('batch_spec_name', metavar='Batch Name', type=str,
                        help='name for this batch, which should match the batch specification file')

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("--no_slurm", action='store_true',
                        help="don't use the Slurm job manager")

    parser.add_argument("--save_to_s3", dest="save_to_s3", action='store_true',
                        help="Move model instance and progress files from local workspace to s3 buckets")

    parser.add_argument("--log_level", nargs=None, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="change logging level to {debug, info, warning, error, critical}")

    return parser.parse_args()


if __name__ == '__main__':
    opts = parse_cli_arguments()

    sys.exit(main(opts.batch_spec_name,
                  dryrun=opts.dryrun,
                  no_slurm=opts.no_slurm,
                  save_to_s3=opts.save_to_s3,
                  log_level=opts.log_level))
