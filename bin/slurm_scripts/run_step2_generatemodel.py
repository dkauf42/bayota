#!/usr/bin/env python
"""

Example usage command:
  >> ./bin/slurm_scripts/run_step2_generatemodel.py --dryrun -cn step1_study_control_1ccccab7-dfbe-4974-86ed-5744b659f938
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

from bayota_util.s3_operations import get_workspace_from_s3, get_s3_modelinstancs_dir, \
    get_s3_control_dir, move_controlfile_to_s3, establish_s3_connection


def main(control_file, dryrun=False, s3_workspace_dir=None, log_level='INFO') -> int:
    if not not s3_workspace_dir:
        get_workspace_from_s3(log_level, s3_workspace_dir)
    else:
        print('<< no s3 workspace directory provided. '
              'defaulting to using local workspace for run_step2_generatemodel.py >>')

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

    # Connection with S3 is established.
    s3ops = establish_s3_connection(log_level, logger)

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
    save_model_pickle(model=my_model, savepath=savepath, dryrun=dryrun)
    logger.info(f"*model saved as pickle to {savepath}*")

    # Model is moved to s3.
    move_model_pickle_to_s3(logger, get_s3_modelinstancs_dir(), s3ops, savepath)

    # Progress report is finalized with timestamp and saved.
    progress_dict['run_timestamps']['step2_generatemodel_done'] = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    progress_file_name = write_progress_file(progress_dict, control_name=control_dict['study']['uuid'])
    if not not s3_workspace_dir:
        move_controlfile_to_s3(logger, get_s3_control_dir(), s3ops,
                               controlfile_name=progress_file_name, no_s3=False, )

    return 0  # a clean, no-issue, exit


def move_model_pickle_to_s3(logger, s3_model_instances_dir, s3ops, savepath):
    """ The local control file is copied to the S3-based workspace. """
    modelinstance_s3path = s3_model_instances_dir + os.path.basename(savepath)
    s3ops.move_to_s3(local_path=savepath, destination_path=f"{modelinstance_s3path}")


def parse_cli_arguments():
    """ Input arguments are parsed. """
    parser = ArgumentParser()

    parser.add_argument("-cn", "--control_filename", dest="control_filename", default=None,
                               help="name for this study's control file")

    parser.add_argument("--s3workspace", dest="s3_workspace_dir",
                        help="path to the workspace copy in an s3 bucket")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("--log_level", nargs=None, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="change logging level to {debug, info, warning, error, critical}")

    return parser.parse_args()


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(control_file=opts.control_filename,
                  dryrun=opts.dryrun,
                  s3_workspace_dir=opts.s3_workspace_dir,
                  log_level=opts.log_level))
