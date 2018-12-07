#!/usr/bin/env python

"""
Example usage command:

"""
import os
import sys
import time
import logging
from argparse import ArgumentParser
import cloudpickle
import json

from efficiencysubproblem.src.spec_handler import notdry
from efficiencysubproblem.src.solver_handling import solvehandler

from bayota_settings.config_script import set_up_logger, get_model_instances_dir, get_output_dir

logger = logging.getLogger('root')
if not logger.hasHandlers():
    set_up_logger()
    logger = logging.getLogger(__name__)


def main(saved_model_file=None, model_modification=None, trial_name=None, dryrun=False):
    logprefix = '** Single Trial **: '

    mdlhandler = None
    if notdry(dryrun, logger, '--Dryrun-- Would load model from pickle with name <%s>' % saved_model_file):
        starttime_modelload = time.time()  # Wall time - clock starts.
        with open(saved_model_file, "rb") as f:
            mdlhandler = cloudpickle.load(f)
        timefor_modelload = time.time() - starttime_modelload  # Wall time - clock stops.
        logger.info('%s model loading (from pickle) done* <- it took %f seconds>' %
                    (logprefix, timefor_modelload))

    # Make Modification
    if not not model_modification:
        modvar = model_modification['variable']
        varvalue = model_modification['value']
        varindexer = model_modification['indexer']

        if not varindexer:
            if notdry(dryrun, logger, '--Dryrun-- Would make model modification; '
                                      'setting %s to %s (no index)' %
                                      (modvar, varvalue)):
                setattr(mdlhandler.model, modvar, varvalue)
        else:
            if notdry(dryrun, logger, '--Dryrun-- Would make model modification; '
                                      'setting %s to %s (at index %s)' %
                                      (modvar, varvalue, varindexer)):
                mdlhandler.model.component(modvar)[varindexer] = varvalue

    modelname = os.path.splitext(os.path.basename(saved_model_file))[0]
    notreal_notimestamp_outputdfpath = os.path.join(get_output_dir(),
                                f"solution_model--{modelname}--_{trial_name}_<timestamp>.csv")
    if notdry(dryrun, logger, '--Dryrun-- Would run trial and save outputdf at: %s' %
                              notreal_notimestamp_outputdfpath):
        solution_dict = solvehandler.basic_solve(modelhandler=mdlhandler, mdl=mdlhandler.model, )
        logger.info(f"{logprefix} Trial '{trial_name}' is DONE "
                    f"(@{solution_dict['timestamp']})! "
                    f"<Solution feasible? --> {solution_dict['feasible']}> ")

        solution_dict['solution_df']['feasible'] = solution_dict['feasible']

        outputdfpath = os.path.join(get_output_dir(), f"solutiondf_{modelname}_{trial_name}_{solution_dict['timestamp']}.csv")
        solution_dict['solution_df'].to_csv(outputdfpath)
        logger.info(f"<Solution written to: {outputdfpath}>")


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()

    # Arguments for top-level
    one_or_the_other_savemodel = parser.add_mutually_exclusive_group()
    one_or_the_other_savemodel.add_argument("-sn", "--saved_model_name", dest="saved_model_name",
                                            help="name for the saved (pickled) model file")
    one_or_the_other_savemodel.add_argument("-sf", "--saved_model_filepath", dest="saved_model_filepath",
                                            help="path for the saved (pickled) model file")

    parser.add_argument("-m", "--model_modification", dest='model_modification',
                        help="modifications to be made to the model after loading and before solving trial instance")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without sending any slurm commands")

    parser.add_argument("-tn", "--trial_name", dest='trial_name',
                        help="unique name to identify this trial (used for saving results)")

    parser.add_argument("-v", "--verbose", dest='verbose',
                        action="count", default=0)

    opts = parser.parse_args()

    # MODEL SAVE FILE
    if not opts.saved_model_filepath:  # name was specified
        opts.saved_model_file = os.path.join(get_model_instances_dir(), opts.saved_model_name + '.yaml')
    else:  # filepath was specified
        opts.saved_model_file = opts.saved_model_filepath

    # convert modification string into a proper dictionary
    opts.model_modification = json.loads(opts.model_modification)

    print(opts)
    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(saved_model_file=opts.saved_model_file,
                  model_modification=opts.model_modification,
                  trial_name=opts.trial_name,
                  dryrun=opts.dryrun))
