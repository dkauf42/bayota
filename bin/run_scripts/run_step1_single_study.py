#!/usr/bin/env python
"""
Note: This submits a SLURM "srun" command to launch the 'step2_generatemodel' script,
      if CLI argument '--no_slurm' is not passed.

Example usage command:
  >> ./bin/run_scripts/run_step1_single_study.py --dryrun -cf ~/bayota_ws_0.1a1.dev4/control/step1_study_control_1ccccab7-dfbe-4974-86ed-5744b659f938.yaml
================================================================================
"""

import os
import sys
import uuid
import yaml
import datetime
import subprocess
from argparse import ArgumentParser

from bayom_e.src.spec_handler import read_spec, notdry

from bayota_settings.base import get_output_dir, get_scripts_dir, get_model_instances_dir, \
    get_bayota_version, get_experiment_specs_dir, \
    get_control_dir, get_model_specs_dir
from bayota_settings.log_setup import set_up_detailedfilelogger
from bayota_util.str_manip import compact_capitalized_geography_string

outdir = get_output_dir()

model_generator_script = os.path.join(get_scripts_dir(), 'run_step2_generatemodel.py')
experiment_script = os.path.join(get_scripts_dir(), 'run_step3_conductexperiment.py')


def main(control_file=None, dryrun=False, no_slurm=False, log_level='INFO') -> int:
    version = get_bayota_version()

    # Load and save new control file
    experiments, \
    baseloadingfilename, \
    control_dict, \
    geography_name, \
    compact_geo_entity_str, \
    model_spec_name, \
    studyshortname, \
    studyid = read_control_file(control_file, version)

    logger = set_up_detailedfilelogger(loggername=studyshortname,  # same name as module, so logger is shared
                                       filename=f"bayota_step1_s{studyid}_{compact_geo_entity_str}.log",
                                       level=log_level,
                                       also_logtoconsole=True,
                                       add_filehandler_if_already_exists=True,
                                       add_consolehandler_if_already_exists=False)

    logger.info('----------------------------------------------')
    logger.info('******* %s *******' % ('BayOTA version ' + version).center(30, ' '))
    logger.info('*************** Single Study *****************')
    logger.info('----------------------------------------------')

    logger.info(f"Geography = {geography_name}")
    logger.info(f"Model specification name = {model_spec_name}")
    logger.info(f"Experiments = {experiments}")
    logger.info(f"Base_loading_file_name = {baseloadingfilename}")

    # A shell command is built for this job submission.
    CMD = f"{model_generator_script} -cf {control_file} --log_level={log_level}"
    if not no_slurm:
        srun_opts = f"--nodes={1} " \
                    f"--ntasks={1} " \
                    f"--exclusive "
        CMD = "srun " + srun_opts + CMD

    # Job is submitted (to generate the model).
    logger.info(f'Job command is: "{CMD}"')
    if notdry(dryrun, logger, '--Dryrun-- Would submit command, then wait.'):
        p1 = subprocess.Popen([CMD], shell=True)
        p1.wait()
        # Get return code from process
        return_code = p1.returncode
        if p1.returncode != 0:
            logger.error(f"Model Generator finished with non-zero code <{return_code}>")
            return 1

    # A job is submitted for each experiment in the list.
    p_list = []
    for ii, exp in enumerate(experiments):
        expid = '{:04}'.format(ii+1)
        logger.info(f"Exp. #{expid}: {exp}")

        expspec_file = os.path.join(get_experiment_specs_dir(), exp)
        expactiondict = read_spec(expspec_file + '.yaml')

        # Generate an experiment control file with a unique identifier (uuid4), by adding onto the study control file
        unique_control_file = os.path.join(get_control_dir(), 'step3_experiment_control_' + str(uuid.uuid4()) + '.yaml')
        try:
            del control_dict["experiments"]
        except KeyError:
            logger.info("Key 'experiments' not found")
        control_dict['experiment_file'] = expspec_file
        expactiondict['id'] = expid
        control_dict['experiment'] = expactiondict
        with open(unique_control_file, "w") as f:
            yaml.safe_dump(control_dict, f, default_flow_style=False)

        # A shell command is built for this job submission.
        CMD = f"{experiment_script}  -cf {unique_control_file} --log_level={log_level}"
        if no_slurm:
            CMD = CMD + " --no_slurm"

        # Job is submitted.
        logger.info(f'Job command is: "{CMD}"')
        if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
            p_list.append(subprocess.Popen([CMD], shell=True))

    if notdry(dryrun, logger, '--Dryrun-- Would wait'):
        [p.wait() for p in p_list]

    return 0  # a clean, no-issue, exit


def read_control_file(control_file, version):
    if not control_file:
        raise ValueError('A control file must be specified.')

    control_dict = read_spec(control_file)

    studydict = control_dict['study']
    studyshortname = studydict['studyshortname']
    studyid = studydict['id']

    # Geography
    geodict = control_dict['geography']
    geo_entity_name = geodict['entity']
    compact_geo_entity_str = compact_capitalized_geography_string(geo_entity_name)
    geodict['shortname'] = compact_geo_entity_str
    control_dict['geography'] = geodict

    # Model Specification
    model_spec_name = studydict['model_spec']
    model_spec_file = os.path.join(get_model_specs_dir(), model_spec_name + '.yaml')
    model_dict = read_spec(model_spec_file)  # Model generation details are saved to control file.
    saved_model_file_for_this_study = os.path.join(get_model_instances_dir(),
                                                   'modelinstance_' + model_spec_name + '_' + compact_geo_entity_str + '.pickle')
    control_dict['model'] = {'spec_file': model_spec_file,
                             'objectiveshortname': model_dict['objectiveshortname'],
                             'constraintshortname': model_dict['constraintshortname'],
                             'saved_file_for_this_study': saved_model_file_for_this_study}

    # Experiments
    experiments = studydict['experiments']
    control_dict['experiments'] = experiments

    # Base Loading Condition
    baseloadingfilename = studydict['base_loading_file_name']
    control_dict['base_loading_file_name'] = baseloadingfilename

    # Run log
    control_dict['code_version']: version
    control_dict['run_timestamps']['step1_study'] = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')

    # Write (or replace existing) study control file with updated dictionary entries
    with open(control_file, "w") as f:
        yaml.safe_dump(control_dict, f, default_flow_style=False)

    return experiments, baseloadingfilename, control_dict, \
           geo_entity_name, compact_geo_entity_str, model_spec_name, studyshortname, studyid


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()

    parser.add_argument("-cf", "--control_filepath", dest="control_filepath", required=True,
                        help="path for this study's control file")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("--no_slurm", action='store_true',
                        help="don't use AWS or slurm facilities")

    parser.add_argument("--log_level", nargs=None, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="change logging level to {debug, info, warning, error, critical}")

    opts = parser.parse_args()

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    sys.exit(main(control_file=opts.control_filepath,
                  dryrun=opts.dryrun, no_slurm=opts.no_slurm,
                  log_level=opts.log_level))
