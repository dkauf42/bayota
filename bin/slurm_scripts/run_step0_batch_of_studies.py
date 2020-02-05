#!/usr/bin/env python
"""
Note: This submits a SLURM "sbatch" command to launch the 'step1_single_study' script,
      if CLI argument '--no_slurm' is not passed.

Example usage command:
  >> ./bin/slurm_scripts/run_step0_batch_of_studies.py --dryrun -n maryland_counties
================================================================================
"""

import os
import sys
import datetime
import subprocess
from argparse import ArgumentParser

from bayota_util.spec_and_control_handler import notdry, parse_batch_spec, write_control_with_uniqueid
from bayota_settings.base import get_bayota_version, get_scripts_dir
from bayota_settings.log_setup import root_logger_setup

single_study_script = os.path.join(get_scripts_dir(), 'run_step1_single_study.py')


def main(batch_spec_name, dryrun=False, no_slurm=False, log_level='INFO') -> int:
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

    # SLURM job submission parameters are specified.
    NUM_NODES = 1
    NUM_TASKS = 32
    NUM_CORES = 32
    PRIORITY = 5000

    # Study pairs (Geography, Model+Experiments) are submitted as SLURM "sbatch" jobs.
    for index, sp in enumerate(study_pairs):
        studyid = '{:04}'.format(index+1)
        geoname = sp[0]
        filesafegeostring = geoname.replace(' ', '').replace(',', '')
        studyspecdict = sp[1]
        spname = filesafegeostring + f"_s{studyid}"
        studyspecdict['studyshortname'] = spname
        studyspecdict['id'] = studyid

        # A study control ("studycon") file w/unique identifier (uuid4) is created.
        control_dict = {"geography": {'scale': geo_scale, 'entity': geoname},
                        "study": studyspecdict, "control_options": control_options,
                        "code_version": version,
                        "run_timestamps": {'step0_batch': datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}}
        unique_control_name = write_control_with_uniqueid(control_dict=control_dict,
                                                          control_name_prefix='step1_studycon')

        logger.debug(f"control file is {unique_control_name}")

        # A shell command is built for this job submission.
        CMD = f"{single_study_script} -cn {unique_control_name} --log_level={log_level}"
        if not no_slurm:
            sbatch_opts = f"--job-name={spname} " \
                          f"--nice={PRIORITY} " \
                          f"--cpus-per-task={2} " \
                          f"--nodes={NUM_NODES} " \
                          f"--ntasks={NUM_TASKS} " \
                          f"--ntasks-per-node={NUM_CORES} " \
                          f"--output=slurm_job_{spname}_%j-%2t.out " \
                          f"--error=slurm_job_{spname}_%j-%2t.err " \
                          f"--time=12:00:00 "  # time requested in hour:minute:second
            CMD = "sbatch " + sbatch_opts + CMD
        else:
            CMD = CMD + " --no_slurm"

        # Job is submitted.
        logger.info(f'Job command is: "{CMD}"')
        if notdry(dryrun, logger, '--Dryrun- Would submit command'):
            subprocess.Popen([CMD], shell=True)

    return 0  # a clean, no-issue, exit


def parse_cli_arguments():
    """ Input arguments are parsed. """
    parser = ArgumentParser()
    parser.add_argument("-n", "--batch_spec_name", dest="batch_spec_name", default=None,
                        help="name for this batch, which should match the batch specification file")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("--no_slurm", action='store_true',
                        help="don't use AWS or slurm facilities")

    parser.add_argument("--log_level", nargs=None, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="change logging level to {debug, info, warning, error, critical}")

    return parser.parse_args()


if __name__ == '__main__':
    opts = parse_cli_arguments()

    sys.exit(main(opts.batch_spec_name,
                  dryrun=opts.dryrun, no_slurm=opts.no_slurm,
                  log_level=opts.log_level))
