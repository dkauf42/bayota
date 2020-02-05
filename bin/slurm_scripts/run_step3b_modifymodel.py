#!/usr/bin/env python
"""
Note: No SLURM commands are submitted within this script.

Example usage command:
  >> ./bin/slurm_scripts/run_step3b_modifymodel.py
================================================================================
"""
import sys
from argparse import ArgumentParser

from bayota_util.spec_and_control_handler import notdry, read_expcon_file
from bayom_e.model_handling.utils import modify_model, save_model_pickle, load_model_pickle

from bayota_settings.log_setup import set_up_detailedfilelogger

from bayota_util.s3_operations import get_workspace_from_s3

logprefix = '** Modifying Model **: '


def main(control_file, s3_workspace_dir=None, dryrun=False, log_level='INFO'):
    if not not s3_workspace_dir:
        get_workspace_from_s3(log_level, s3_workspace_dir)
    else:
        print('<< no s3 workspace directory provided. '
              'defaulting to using local workspace for run_step2_generatemodel.py >>')

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