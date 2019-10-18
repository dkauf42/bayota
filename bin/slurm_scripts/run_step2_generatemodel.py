#!/usr/bin/env python
"""
Note: No SLURM commands are submitted within this script.

Example usage command:
  >> ./bin/slurm_scripts/run_step2_generatemodel.py --dryrun -cf ~/bayota_ws_0.1a1.dev4/control/step1_study_control_1ccccab7-dfbe-4974-86ed-5744b659f938.yaml
================================================================================
"""

import os
import sys
import time
from argparse import ArgumentParser

from bayom_e.model_handling.interface import build_model
from bayota_util.spec_handler import notdry, read_model_controlfile

from bayom_e.model_handling.utils import save_model_pickle

from bayota_settings.base import get_model_specs_dir,\
    get_model_instances_dir, get_workspace_dir, get_control_dir
from bayota_settings.log_setup import set_up_detailedfilelogger

from bayota_util.s3_operations import S3ops


def main(geography_name, model_spec_file, control_file=None,
         saved_model_file=None, dryrun=False, baseloadingfilename='', s3_workspace_dir=None,
         log_level='INFO') -> int:

    if not not s3_workspace_dir:
        """ Workspace is copied in full from S3 """
        try:
            s3ops = S3ops(bucketname='modeling-data.chesapeakebay.net', log_level=log_level)
        except EnvironmentError as e:
            print(e)
            print('run_step2_generatemodel; trying again')
            try:
                s3ops = S3ops(bucketname='modeling-data.chesapeakebay.net', log_level=log_level)
            except EnvironmentError as e:
                print(e)
                raise e
        # Workspace is copied.
        s3ops.get_from_s3(s3path=s3_workspace_dir,
                          local_path=get_workspace_dir(),
                          move_directory=True)
        print(f"copied s3 workspace from {s3_workspace_dir} to local location: {get_workspace_dir()}")
    else:
        print('<< no s3 workspace directory provided. '
              'defaulting to using local workspace for run_step2_generatemodel.py >>')

    baseloadingfilename, \
    compact_geo_entity_str, \
    geography_entity, \
    geography_scale, \
    model_spec_file, \
    saved_model_file, \
    savedata2file = read_model_controlfile(baseloadingfilename,
                                           control_file,
                                           geography_name,
                                           model_spec_file,
                                           saved_model_file)

    logger = set_up_detailedfilelogger(loggername=os.path.splitext(os.path.basename(model_spec_file))[0],
                                       filename=f"step2_modelgeneration_{compact_geo_entity_str}.log",
                                       level=log_level,
                                       also_logtoconsole=True,
                                       add_filehandler_if_already_exists=True,
                                       add_consolehandler_if_already_exists=False)

    logger.info('----------------------------------------------')
    logger.info('************** Model Generation **************')
    logger.info('----------------------------------------------')

    logger.info('Geographies specification: %s' % geography_entity)

    if not saved_model_file:
        savepath = os.path.join(get_model_instances_dir(), 'saved_instance.pickle')
    else:
        savepath = saved_model_file

    my_model = None
    if notdry(dryrun, logger, '--Dryrun-- Would generate model'):
        starttime_modelinstantiation = time.time()  # Wall time - clock starts.

        my_model, dataplate = build_model(model_spec=model_spec_file,
                                          geoscale=geography_scale.lower(),
                                          geoentities=geography_entity,
                                          savedata2file=savedata2file,
                                          baseloadingfilename=baseloadingfilename)

        timefor_modelinstantiation = time.time() - starttime_modelinstantiation  # Wall time - clock stops.
        logger.info('*model instantiation done* <- it took %f seconds>' % timefor_modelinstantiation)

    save_model_pickle(model=my_model, savepath=savepath, dryrun=dryrun)
    logger.info(f"*model saved as pickle to {savepath}*")

    return 0  # a clean, no-issue, exit


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()

    # Arguments for top-level
    one_or_the_other = parser.add_mutually_exclusive_group()
    one_or_the_other.add_argument("-n", "--model_spec_name", dest="model_name", default=None,
                                  help="name for this model, which should match the model specification file")
    one_or_the_other.add_argument("-f", "--model_spec_filepath", dest="model_spec_filepath", default=None,
                                  help="path for this model's specification file")
    one_or_the_other.add_argument("-cf", "--control_filepath", dest="control_filepath", default=None,
                                  help="path for this study's control file")
    one_or_the_other.add_argument("-cn", "--control_filename", dest="control_filename", default=None,
                                  help="name for this study's control file")

    parser.add_argument("-g", "--geography", dest="geography_name",
                        help="name for a geography defined in geography_specs.yaml")

    one_or_the_other_savemodel = parser.add_mutually_exclusive_group()
    one_or_the_other_savemodel.add_argument("-sn", "--saved_model_name", dest="saved_model_name",
                                            help="name for the saved (pickled) model file")
    one_or_the_other_savemodel.add_argument("-sf", "--saved_model_filepath", dest="saved_model_filepath",
                                            help="path for the saved (pickled) model file")

    parser.add_argument("-bl", "--base_loading", dest="baseloadingfilename",
                        help="name of the base loading file to read from data/raw")

    parser.add_argument("--s3workspace", dest="s3_workspace_dir",
                        help="path to the workspace copy in an s3 bucket")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("--log_level", nargs=None, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="change logging level to {debug, info, warning, error, critical}")

    opts = parser.parse_args()

    if not opts.control_filepath:  # control file was not specified
        if not opts.control_filename:
            # MODEL SPEC
            if not opts.model_spec_filepath:  # name was specified
                opts.model_spec_file = os.path.join(get_model_specs_dir(), opts.model_name + '.yaml')
            else:  # filepath was specified
                opts.model_spec_file = opts.model_spec_filepath

            # MODEL SAVE FILE
            if not opts.saved_model_filepath:  # name was specified
                opts.saved_model_file = os.path.join(get_model_instances_dir(), opts.saved_model_name + '.yaml')
            else:  # filepath was specified
                opts.saved_model_file = opts.saved_model_filepath
        else:
            opts.control_filepath = os.path.join(get_control_dir(), opts.control_filename + '.yaml')
            opts.model_spec_file = None
            opts.saved_model_file = None
    else:
        opts.model_spec_file = None
        opts.saved_model_file = None

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(opts.geography_name, opts.model_spec_file,
                  control_file=opts.control_filepath,
                  saved_model_file=opts.saved_model_file,
                  dryrun=opts.dryrun,
                  baseloadingfilename=opts.baseloadingfilename,
                  s3_workspace_dir=opts.s3_workspace_dir,
                  log_level=opts.log_level))
