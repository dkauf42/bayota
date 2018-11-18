#!/usr/bin/env python

"""
Example usage command:
    ./bin/scripts_by_level/run_single_study.py --dryrun -f /Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/bayota/bin/study_specs/single_study_specs/adamsPA_0001.yaml
"""

import os
import sys
import logging
import subprocess
from argparse import ArgumentParser

from efficiencysubproblem.src.spec_handler import read_spec, notdry

from bayota_settings.config_script import get_output_dir, get_scripts_dir, get_model_instances_dir, \
    set_up_logger, get_bayota_version, get_single_study_specs_dir, get_experiment_specs_dir

logger = logging.getLogger('root')
if not logger.hasHandlers():
    set_up_logger()
    logger = logging.getLogger(__name__)

outdir = get_output_dir()

model_generator_script = os.path.join(get_scripts_dir(), 'run_generatemodel.py')
experiment_script = os.path.join(get_scripts_dir(), 'run_conductexperiment.py')


def main(study_spec_file, geography_name, dryrun=False):

    studydict = read_spec(study_spec_file)
    model_spec_name = studydict['model_spec']
    EXPERIMENTS = studydict['experiments']

    saved_model_file_for_this_study = os.path.join(get_model_instances_dir(),
                                                   'saved_instance' + model_spec_name + '_' + geography_name + '.pickle')

    version = get_bayota_version()

    logger.info('----------------------------------------------')
    logger.info('*********** BayOTA version %s *************' % version)
    logger.info('******* Single Study: Model Generation *******')
    logger.info('----------------------------------------------')

    logger.info('Geography for this study: %s' % geography_name)
    logger.info('Model for this study: %s' % model_spec_name)
    logger.info('Experiments in study spec: %s' % EXPERIMENTS)

    # Create a task to submit to the queue
    CMD = "srun "
    CMD += "%s -g %s -n %s -sf %s" % (model_generator_script, geography_name,
                                      model_spec_name, saved_model_file_for_this_study)
    # Submit the job
    p1 = None
    logger.info('Job command is: "%s"' % CMD)
    if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
        p1 = subprocess.Popen([CMD], shell=True)
    if notdry(dryrun, logger, '--Dryrun-- Would wait'):
        p1.wait()

    logger.info('----------------------------------------------')
    logger.info('******* Single Study: Experiments Loop *******')
    logger.info('----------------------------------------------')

    for ii, exp in enumerate(EXPERIMENTS):
        logger.info('Exp. #%d: %s' % (ii+1, exp))

        expspec_file = os.path.join(get_experiment_specs_dir(), exp)
        # Create a task to submit to the queue
        CMD = "srun "
        CMD += "%s -n %s -sf %s" % (experiment_script, expspec_file,
                                    saved_model_file_for_this_study)
        # Submit the job
        p1 = None
        logger.info('Job command is: "%s"' % CMD)
        if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
            p1 = subprocess.Popen([CMD], shell=True)
        if notdry(dryrun, logger, '--Dryrun-- Would wait'):
            p1.wait()

    return 0  # a clean, no-issue, exit


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()
    one_or_the_other = parser.add_mutually_exclusive_group(required=True)
    one_or_the_other.add_argument("-n", "--study_name", dest="study_name", default=None,
                                  help="name for this study, which should match the study specification file")
    one_or_the_other.add_argument("-f", "--study_spec_filepath", dest="study_spec_filepath", default=None,
                                  help="path for this study's specification file")

    parser.add_argument("-g", "--geography", dest="geography_name",
                        help="name for a geography defined in geography_specs.yaml")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without sending any slurm commands")

    opts = parser.parse_args()

    if not opts.study_spec_filepath:  # study name was specified
        opts.study_spec_file = os.path.join(get_single_study_specs_dir(), opts.study_name + '.yaml')
    else:  # study filepath was specified
        opts.study_spec_file = opts.study_spec_filepath

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    sys.exit(main(opts.study_spec_file, opts.geography_name, dryrun=opts.dryrun))
