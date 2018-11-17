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

from efficiencysubproblem.src.spec_handler import read_spec, notdry
from efficiencysubproblem.src.solver_handling import solvehandler

from bayota_settings.config_script import set_up_logger, get_source_pickles_dir
# set_up_logger()
# logger = logging.getLogger(__name__)
# logger = logging.getLogger('root')

logger = logging.getLogger('root')
if not logger.hasHandlers():
    set_up_logger()
    logger = logging.getLogger(__name__)


savepath = os.path.join(get_source_pickles_dir(), 'saved_instance.pickle')


def main(saved_model_file=None, model_modification=None, dryrun=False):

    logger.info('----------------------------------------------')
    logger.info('*************** Single Trial *****************')
    logger.info('----------------------------------------------')

    mdlhandler = None
    if notdry(dryrun, logger, '--Dryrun-- Would load model from pickle with name <%s>' % savepath):
        starttime_modelload = time.time()  # Wall time - clock starts.
        with open(savepath, "rb") as f:
            mdlhandler = cloudpickle.load(saved_model_file, f)
        timefor_modelload = time.time() - starttime_modelload  # Wall time - clock stops.
        logger.info('*model loading (from pickle) done* <- it took %f seconds>' % timefor_modelload)

    if notdry(dryrun, logger, '--Dryrun-- Would run trial'):
        # TRIALS = read_spec(experiment_spec_file)['trials']
        # logger.info('\tTrials to be conducted: %s' % TRIALS)
        # for trial in TRIALS:
        #     # Create a task to submit to the queue
        #     CMD = "srun "
        #     CMD += "%s -n %s -sf %s" % (experiment_script, expspec_file, saved_model_file)
        #     # Submit the job
        #     logger.info('Job command is: "%s"' % CMD)
        #     if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
        #         p_list.append(subprocess.Popen([CMD], shell=True))

        # Make Modification
        if not not model_modification:
            varname = model_modification['variable']
            varvalu = model_modification['value']

            mdlhandler.model.component(varname)['N'] = varvalu
            mdlhandler.model.component(varname).pprint()

        solution_dict = solvehandler.basic_solve(modelhandler=mdlhandler, mdl=mdlhandler.model, )
        logger.info("<My Trial is DONE!>")
        logger.info(solution_dict)

        # list_of_trialdicts = read_spec(experiment_spec_file)['trials']
        # logger.info('\tTrials to be conducted: %s' % list_of_trialdicts)
        # for i, dictwithtrials in enumerate(list_of_trialdicts):
        #     logger.info('trial set #%d: %s' % (i, dictwithtrials))
        #     for k, v in dictwithtrials.items():
        #         logger.info('variable to modify: %s' % k)
        #         # mdlhandler.model.component(k).pprint()
        #         # mdlhandler.model.component(k)._index.pprint()
        #         logger.info('values: %s' % v)
        #         for j, vi in enumerate(v):
        #             logger.info('trial #%d, setting <%s> to <%s>' % (j, k, vi))
        #             mdlhandler.model.component(k)['N'] = vi
        #             mdlhandler.model.component(k).pprint()
        #
        #             solution_dict = solvehandler.basic_solve(modelhandler=mdlhandler, mdl=mdlhandler.model, )
        #
        #             break
        #     break


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

    parser.add_argument("-v", "--verbose", dest='verbose',
                        action="count", default=0)

    opts = parser.parse_args()

    # MODEL SAVE FILE
    if not opts.saved_model_filepath:  # name was specified
        opts.saved_model_file = os.path.join(get_source_pickles_dir(), opts.saved_model_name + '.yaml')
    else:  # filepath was specified
        opts.saved_model_file = opts.saved_model_filepath

    # convert modification string into a proper dictionary
    opts.model_modification = json.loads(opts.model_modification)

    print(opts)
    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(saved_model_file=opts.saved_model_file, model_modification=opts.model_modification, dryrun=opts.dryrun))
