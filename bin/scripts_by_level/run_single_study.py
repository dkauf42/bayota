#!/usr/bin/env python

"""
Example usage command:
    ./bin/scripts_by_level/run_single_study.py --dryrun -f /Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/bayota/bin/study_specs/single_study_specs/adamsPA_0001.yaml
"""

import os
import sys
import yaml
import logging
import subprocess
from argparse import ArgumentParser

from efficiencysubproblem.src.spec_handler import read_spec, notdry

from bayota_settings.config_script import get_output_dir, get_scripts_dir, get_model_instances_dir, \
    set_up_logger, get_bayota_version, get_single_study_specs_dir, get_experiment_specs_dir, \
    get_control_dir

logger = logging.getLogger('root')
if not logger.hasHandlers():
    set_up_logger()
    logger = logging.getLogger(__name__)

outdir = get_output_dir()

model_generator_script = os.path.join(get_scripts_dir(), 'run_generatemodel.py')
experiment_script = os.path.join(get_scripts_dir(), 'run_conductexperiment.py')


def main(study_spec_file, geography_name, control_file=None,
         dryrun=False, no_slurm=False):
    logprefix = '** Single Study **: '

    version = get_bayota_version()

    logger.info('----------------------------------------------')
    logger.info('*********** BayOTA version %s *************' % version)
    logger.info('*************** Single Study *****************')
    logger.info('----------------------------------------------')

    if not not control_file:
        control_dict = read_spec(control_file)

        study_spec_file = os.path.join(get_single_study_specs_dir(), control_dict['study_spec'] + '.yaml')
        geography_name = control_dict['geography_entity']
    else:
        control_dict = dict()

    # read from study specification file (and add those entries to the unique control file)
    studydict = read_spec(study_spec_file)
    #
    model_spec_name = studydict['model_spec']
    control_dict['model_spec'] = model_spec_name
    #
    EXPERIMENTS = studydict['experiments']
    control_dict['experiments'] = EXPERIMENTS
    #
    baseloadingfilename = studydict['base_loading_file_name']
    control_dict['base_loading_file_name'] = baseloadingfilename
    #
    filesafegeostring = geography_name.replace(' ', '').replace(',', '')
    saved_model_file_for_this_study = os.path.join(get_model_instances_dir(),
                                                   'modelinstance_' + model_spec_name + '_' + filesafegeostring + '.pickle')
    control_dict['saved_model_file_for_this_study'] = saved_model_file_for_this_study

    # Write (or replace existing) control file with updated dictionary entries
    with open(control_file, "w") as f:
        yaml.dump(control_dict, f, default_flow_style=False)

    logger.info(f"{logprefix} Model Generation - Geography = {geography_name}")
    logger.info(f"{logprefix} Model Generation - Spec name = {model_spec_name}")
    logger.info(f"{logprefix} Model Generation - Experiments = {EXPERIMENTS}")
    logger.info(f"{logprefix} Model Generation - base_loading_file_name = {baseloadingfilename}")

    CMD = f"{model_generator_script} -cf {control_file} "
    if not no_slurm:
        # Create a task to submit to the queue
        CMD = "srun " + CMD

    # Submit the job
    p1 = None
    logger.info(f'Job command is: "{CMD}"')
    if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
        p1 = subprocess.Popen([CMD], shell=True)
    if notdry(dryrun, logger, '--Dryrun-- Would wait'):
        p1.wait()

    p_list = []
    for ii, exp in enumerate(EXPERIMENTS):
        logger.info(f"{logprefix} Exp. #{ii+1}: {exp}")

        expspec_file = os.path.join(get_experiment_specs_dir(), exp)

        CMD = f"{experiment_script} -n {expspec_file} -sf {saved_model_file_for_this_study}"
        if not no_slurm:
            # Create a task to submit to the queue
            CMD = "srun " + CMD

        # Submit the job
        p1 = None
        logger.info(f'Job command is: "{CMD}"')
        if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
            p_list.append(subprocess.Popen([CMD], shell=True))
        # if notdry(dryrun, logger, '--Dryrun-- Would wait'):
        #     p_list.append(subprocess.Popen([CMD], shell=True))

    if notdry(dryrun, logger, '--Dryrun-- Would wait'):
        [p.wait() for p in p_list]

    return 0  # a clean, no-issue, exit


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()
    one_or_the_other = parser.add_mutually_exclusive_group(required=True)
    one_or_the_other.add_argument("-n", "--study_name", dest="study_name", default=None,
                                  help="name for this study, which should match the study specification file")
    one_or_the_other.add_argument("-f", "--study_spec_filepath", dest="study_spec_filepath", default=None,
                                  help="path for this study's specification file")
    one_or_the_other.add_argument("-cf", "--control_filepath", dest="control_filepath", default=None,
                                  help="path for this study's control file")

    parser.add_argument("-g", "--geography", dest="geography_name",
                        help="name for a geography defined in geography_specs.yaml")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("--no_slurm", action='store_true',
                        help="don't use AWS or slurm facilities")

    opts = parser.parse_args()

    if not opts.study_spec_filepath:
        if not opts.study_name:  # control file was specified
            controldict = read_spec(opts.control_filepath)
            opts.study_spec_file = os.path.join(get_single_study_specs_dir(),
                                                controldict['study_spec'] + '.yaml')
            opts.geography_name = controldict['geography_entity']
        else:  # study name was specified
            opts.study_spec_file = os.path.join(get_single_study_specs_dir(), opts.study_name + '.yaml')
    else:  # study filepath was specified
        opts.study_spec_file = opts.study_spec_filepath

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    sys.exit(main(opts.study_spec_file, opts.geography_name, control_file=opts.control_filepath,
                  dryrun=opts.dryrun, no_slurm=opts.no_slurm))
