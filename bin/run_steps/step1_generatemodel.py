#!/usr/bin/env python
"""

Example usage command:
  >> ./bin/slurm_run_scripts/step1_generatemodel.py --dryrun -cn step1_study_control_1ccccab7-dfbe-4974-86ed-5744b659f938
================================================================================
"""

import os
import sys
import time
import datetime
from argparse import ArgumentParser

from bayom_e.model_handling.interface import build_model
from bayota_util.spec_and_control_handler import notdry, read_model_controlfile, write_progress_file

from bayom_e.model_handling.utils import save_model_pickle

from bayota_settings.base import get_model_instances_dir
from bayota_settings.log_setup import set_up_detailedfilelogger

from bayota_util.s3_operations import establish_s3_connection, pull_control_dir_from_s3, pull_data_dir_from_s3, \
    move_controlfile_to_s3


def main(control_file, dryrun=False, use_s3_ws=False, save_to_s3=False, log_level='INFO') -> int:
    if save_to_s3 or use_s3_ws:
        # Connection with S3 is established.
        s3ops = establish_s3_connection(log_level, logger=None)

    # If using s3, required workspace directories are pulled from buckets.
    if use_s3_ws:
        pull_control_dir_from_s3(log_level=log_level, s3ops=s3ops)
        pull_data_dir_from_s3(log_level=log_level, s3ops=s3ops)

    # Control file is read.
    control_dict, \
    baseloadingfilename, \
    compact_geo_entity_str, \
    geography_entity, \
    geography_scale, \
    model_spec_name, \
    saved_model_name, \
    savedata2file = read_model_controlfile(control_file_name=control_file)

    # Logging formats are set up.
    logger = set_up_detailedfilelogger(loggername=model_spec_name,
                                       filename=f"step2_modelgeneration_{compact_geo_entity_str}.log",
                                       level=log_level,
                                       also_logtoconsole=True,
                                       add_filehandler_if_already_exists=True,
                                       add_consolehandler_if_already_exists=False)
    logger.info('----------------------------------------------')
    logger.info('************** Model Generation **************')
    logger.info(' geographies specification: %s' % geography_entity)
    logger.info('----------------------------------------------')

    # A progress report is started.
    progress_dict = control_dict.copy()
    progress_dict['run_timestamps'] = {'step2_generatemodel_start': datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}

    # Model is generated.
    my_model = None
    if notdry(dryrun, logger, '--Dryrun-- Would generate model'):
        starttime_modelinstantiation = time.time()  # Wall time - clock starts.

        my_model, dataplate = build_model(model_spec_name=model_spec_name,
                                          geoscale=geography_scale.lower(), geoentities=geography_entity,
                                          baseloadingfilename=baseloadingfilename,
                                          savedata2file=savedata2file)

        timefor_modelinstantiation = time.time() - starttime_modelinstantiation  # Wall time - clock stops.
        logger.info('*model instantiation done* <- it took %f seconds>' % timefor_modelinstantiation)

    # Model is saved.
    if not saved_model_name:
        saved_model_name = 'saved_instance.pickle'
    savepath = os.path.join(get_model_instances_dir(), saved_model_name)
    logger.debug(f"*saving model as pickle to {savepath}*")
    save_model_pickle(model=my_model, savepath=savepath, dryrun=dryrun)
    logger.debug(f"*model saved*")

    # If using s3, model instance is moved to bucket.
    if save_to_s3:
        move_model_pickle_to_s3(logger, s3ops, savepath)

    # Progress report is finalized with timestamp and saved.
    progress_dict['run_timestamps']['step2_generatemodel_done'] = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    progress_file_name = write_progress_file(progress_dict, control_name=control_dict['study']['uuid'])
    if save_to_s3:
        move_controlfile_to_s3(logger, s3ops, controlfile_name=progress_file_name, no_s3=False)
    logger.debug(f"*model generation done*")
    return 0  # a clean, no-issue, exit


def move_model_pickle_to_s3(logger, s3ops, savepath):
    """ The local control file is copied to the S3-based workspace. """
    modelinstance_s3path = get_model_instances_dir(s3=True) + os.path.basename(savepath)
    s3ops.move_to_s3(local_path=savepath, destination_path=f"{modelinstance_s3path}")


def parse_cli_arguments():
    """ Input arguments are parsed. """
    parser = ArgumentParser(description="Generate a study's model")

    parser.add_argument("control_filename", metavar='Control Filename', type=str,
                        help="name for this model generation's control file")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("--use_s3_ws", dest="use_s3_ws", action='store_true',
                        help="Pull workspace files from s3 bucket to local workspace at start of running this step")

    parser.add_argument("--save_to_s3", dest="save_to_s3", action='store_true',
                        help="Move model instance and progress files from local workspace to s3 buckets")

    parser.add_argument("--log_level", nargs=None, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="change logging level to {debug, info, warning, error, critical}")

    return parser.parse_args()


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(opts.control_filename,
                  dryrun=opts.dryrun,
                  use_s3_ws=opts.use_s3_ws,
                  save_to_s3=opts.save_to_s3,
                  log_level=opts.log_level))
