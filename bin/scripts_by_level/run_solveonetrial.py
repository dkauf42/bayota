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


savepath = os.path.join(get_model_instances_dir(), 'saved_instance.pickle')


def main(saved_model_file=None, model_modification=None, trial_name=None, dryrun=False):

    logger.info('----------------------------------------------')
    logger.info('*************** Single Trial *****************')
    logger.info('----------------------------------------------')

    mdlhandler = None
    if notdry(dryrun, logger, '--Dryrun-- Would load model from pickle with name <%s>' % savepath):
        starttime_modelload = time.time()  # Wall time - clock starts.
        with open(saved_model_file, "rb") as f:
            mdlhandler = cloudpickle.load(f)
        timefor_modelload = time.time() - starttime_modelload  # Wall time - clock stops.
        logger.info('*model loading (from pickle) done* <- it took %f seconds>' % timefor_modelload)

    if notdry(dryrun, logger, '--Dryrun-- Would run trial'):

        # Make Modification
        if not not model_modification:
            varname = model_modification['variable']
            varvalu = model_modification['value']

            mdlhandler.model.component(varname)['N'] = varvalu
            mdlhandler.model.component(varname).pprint()

        solution_dict = solvehandler.basic_solve(modelhandler=mdlhandler, mdl=mdlhandler.model, )
        logger.info("<My Trial is DONE!>")
        logger.info(f"<Solution feasible? --> {solution_dict['feasible']}>")
        logger.info(f"<Solving occurred at {solution_dict['timestamp']}>")

        outputdfpath = os.path.join(get_output_dir(), f"solutiondf_{trial_name}_{solution_dict['timestamp']}.csv")
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

    parser.add_argument("-tn", "--trial_name", action='trial_name',
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
