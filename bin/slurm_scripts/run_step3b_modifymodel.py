#!/usr/bin/env python
"""
Note: No SLURM commands are submitted within this script.

Example usage command:
  >> ./bin/slurm_scripts/run_step3b_modifymodel.py
================================================================================
"""
import os
import sys
from argparse import ArgumentParser

from bayota_util.spec_handler import notdry, read_expcon_file
from bayom_e.model_handling.utils import modify_model, save_model_pickle, load_model_pickle

from bayota_settings.base import get_workspace_dir, \
    get_model_instances_dir, get_control_dir, get_experiment_specs_dir
from bayota_settings.log_setup import set_up_detailedfilelogger

from bayota_util.s3_operations import S3ops

logprefix = '** Modifying Model **: '

def main(experiment_spec_file, saved_model_file=None, control_file=None, s3_workspace_dir=None,
         dryrun=False, log_level='INFO'):

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

    actionlist, compact_geo_entity_str, control_dict, expid, expname, list_of_trialdicts, saved_model_file, studyid = read_expcon_file(
        control_file, experiment_spec_file, saved_model_file)

    logger = set_up_detailedfilelogger(loggername=expname,  # same name as module, so logger is shared
                                       filename=f"step3_s{studyid}_e{expid}_{compact_geo_entity_str}.log",
                                       level=log_level,
                                       also_logtoconsole=True,
                                       add_filehandler_if_already_exists=True,
                                       add_consolehandler_if_already_exists=False)

    # The model is modified according to specified experiment set-up
    logger.info(f"{logprefix} {expname} - modification action list = {actionlist}")
    if notdry(dryrun, logger, '--Dryrun-- Would modify model with action <%s>' % actionlist):

        # Check whether any model modifications are specified
        if actionlist[0] == 'none':
            logger.info(f"{logprefix} {expname} - no model modifications made")
        else:
            # Load the model object
            my_model = load_model_pickle(savepath=saved_model_file, dryrun=dryrun)

            for a in actionlist:
                modify_model(my_model, actiondict=a)

            save_model_pickle(model=my_model, savepath=saved_model_file, dryrun=dryrun, logprefix=logprefix)


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
    one_or_the_other.add_argument("-cn", "--control_filename", dest="control_filename", default=None,
                                  help="name for this study's control file")

    one_or_the_other_savemodel = parser.add_mutually_exclusive_group()
    one_or_the_other_savemodel.add_argument("-sn", "--saved_model_name", dest="saved_model_name",
                                            help="name for the saved (pickled) model file")
    one_or_the_other_savemodel.add_argument("-sf", "--saved_model_filepath", dest="saved_model_filepath",
                                            help="path for the saved (pickled) model file")

    parser.add_argument("--s3workspace", dest="s3_workspace_dir",
                        help="path to the workspace copy in an s3 bucket")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("--log_level", nargs=None, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="change logging level to {debug, info, warning, error, critical}")

    opts = parser.parse_args()

    if not not opts.control_filepath:  # a control file was specified
        pass
    elif not not opts.control_filename:  # a control filename was specified
        opts.control_filepath = os.path.join(get_control_dir(), opts.control_filename + '.yaml')
    else:
        # EXPERIMENT SPEC
        if not opts.experiment_spec_filepath:  # name was specified instead
            opts.experiment_spec_filepath = os.path.join(get_experiment_specs_dir(), opts.experiment_name + '.yaml')
        # MODEL SAVE FILE
        if not opts.saved_model_filepath:  # name was specified instead
            opts.saved_model_filepath = os.path.join(get_model_instances_dir(), opts.saved_model_name + '.yaml')

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(opts.experiment_spec_filepath,
                  control_file=opts.control_filepath,
                  saved_model_file=opts.saved_model_file,
                  dryrun=opts.dryrun,
                  s3_workspace_dir=opts.s3_workspace_dir,
                  log_level=opts.log_level))