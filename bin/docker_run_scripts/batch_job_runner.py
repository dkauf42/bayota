#!/usr/bin/env python
"""
This submits Docker CMDs to launch the model generation, experiments, and trials.

Example usage command:
  >> ./bin/docker_run_scripts/batch_job_runner.py --dryrun -cf ./bin/study_specs/batch_study_specs/maryland_counties.yaml

# Daniel Kaufman, Chesapeake Research Consortium, Inc.
# 23 August 2019
================================================================================
"""

import os
import sys
import uuid
import yaml
import boto3
import docker
import datetime
import itertools
from argparse import ArgumentParser

from bayota_util.spec_handler import read_spec, notdry
from bayota_settings.base import get_bayota_version, get_model_instances_dir, get_workspace_dir, \
    get_spec_files_dir, get_control_dir, get_model_specs_dir, get_experiment_specs_dir
from bayota_settings.log_setup import root_logger_setup
from bayota_util.str_manip import compact_capitalized_geography_string
from castjeeves.jeeves import Jeeves

s3_client = boto3.client('s3')
batch = boto3.client('batch', region_name='us-east-1')

docker_client = docker.from_env()
docker_image = 'bayota_conda_then_ipopt_app'


def main(batch_spec_file, dryrun=False, log_level='INFO') -> int:
    logger = root_logger_setup(consolehandlerlevel=log_level, filehandlerlevel='DEBUG')
    logger.debug(locals())

    version = get_bayota_version()
    logger.info('v----------------------------------------------v')
    logger.info('******* %s *******' % ('BayOTA version ' + version).center(30, ' '))
    logger.info('************** Batch of studies **************')
    logger.info('^----------------------------------------------^')

    # Batch specification file is read.
    geo_scale, study_pairs, control_options = read_batch_spec_file(batch_spec_file, logger=logger)
    # From the spec, we got:
    #     - list of study specs
    #     - list of geographies
    #     - control options

    # TODO: push the workspace to s3, get path to s3 ws-copy ready for passing to docker image script.
    # TODO: or should we wait to push the ws to s3 until after we create each studycon file?

    # (Geography, Model+Experiments) are combined to form studies, which are submitted as jobs.
    for index, sp in enumerate(study_pairs):
        studyid = '{:04}'.format(index+1)

        # geography
        geoname = sp[0]
        filesafegeostring = geoname.replace(' ', '').replace(',', '')

        # model + experiment
        studyspecdict = sp[1]

        # study ID
        spname = filesafegeostring + f"_s{studyid}"
        studyspecdict['studyshortname'] = spname
        studyspecdict['id'] = studyid

        # A study control ("studycon") file w/unique identifier (uuid4) is created.
        control_dict = {"geography": {'scale': geo_scale, 'entity': geoname},
                        "study": studyspecdict, "control_options": control_options,
                        "code_version": version,
                        "run_timestamps": {'step0_batch': datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}}
        studycon_name = 'step1_studycon' + str(uuid.uuid4()) + '.yaml'
        study_control_file = os.path.join(get_control_dir(), studycon_name)
        with open(study_control_file, "w") as f:
            yaml.safe_dump(control_dict, f, default_flow_style=False)

        # Read the study control file....
        experiments, \
        baseloadingfilename, \
        control_dict, \
        geography_name, \
        compact_geo_entity_str, \
        model_spec_name, \
        studyshortname, \
        studyid = read_study_control_file(study_control_file, version)

        logger.info('v----------------------------------------------v')
        logger.info('*************** Single Study *****************')
        logger.info(f"Geography = {geography_name}")
        logger.info(f"Model specification name = {model_spec_name}")
        logger.info(f"Experiments = {experiments}")
        logger.info(f"Base_loading_file_name = {baseloadingfilename}")
        logger.info('^----------------------------------------------^')

        """ GENERATE MODEL VIA DOCKER IMAGE """
        volumes_dict, env_variables = setup_docker_arguments(logger=logger)
        # A command is built for this job submission.
        model_generator_script = '/root/bayota/bin/slurm_scripts/run_step2_generatemodel.py'
        CMD = f"{model_generator_script} -cf {study_control_file} --log_level={log_level}"
        logger.info(f'For image -- job command is: "{CMD}"')
        # Job is submitted.
        response = docker_client.containers.run(docker_image, CMD,
                                                volumes=volumes_dict,
                                                environment=env_variables)
        logger.info(f"*command submitted to image <{docker_image}>* - response is <{response}>")

        # To use AWS Batch, we submit the job with a job definition/queue specified.
        # response = batch.submit_job(jobName='Model_Generation',
        #                             jobQueue='GIS-Dev-queue',
        #                             jobDefinition='GIS-Merge-Rasters:3',
        #                             containerOverrides={
        #                                     "command": ['python',
        #                                                 f"{model_generator_script}",
        #                                                 f"-cf {study_control_file}",
        #                                                 f"--log_level={log_level}"],
        #                             })
        # print("Job ID is {}.".format(response['jobId']))

        """ CONDUCT EXPERIMENTS VIA DOCKER IMAGE """
        volumes_dict, env_variables = setup_docker_arguments(logger=logger)
        # A job is submitted for each experiment in the list.
        p_list = []
        for ii, exp in enumerate(experiments):
            expid = '{:04}'.format(ii + 1)
            logger.info(f"Exp. #{expid}: {exp}")

            expspec_file = os.path.join(get_experiment_specs_dir(), exp)
            expactiondict = read_spec(expspec_file + '.yaml')

            # An experiment control ("expcon") file w/unique identifier (uuid4) is generated by adding to the studycon file.
            unique_control_file = os.path.join(get_control_dir(), 'step3_expcon' + str(uuid.uuid4()) + '.yaml')
            try:
                del control_dict["experiments"]
            except KeyError:
                logger.info("Key 'experiments' not found")
            control_dict['experiment_file'] = expspec_file
            expactiondict['id'] = expid
            control_dict['experiment'] = expactiondict
            with open(unique_control_file, "w") as f:
                yaml.safe_dump(control_dict, f, default_flow_style=False)

            # A command is built for this job submission.
            experiment_script = '/root/bayota/bin/slurm_scripts/run_step3_conductexperiment.py'
            CMD = f"{experiment_script}  -cf {unique_control_file} --no_slurm --log_level={log_level}"
            logger.info(f'For image -- job command is: "{CMD}"')
            # Job is submitted.
            response = docker_client.containers.run(docker_image, CMD,
                                                    volumes=volumes_dict,
                                                    environment=env_variables)
            logger.info(f"*command submitted to image <{docker_image}>* - response is <{response}>")

    return 0  # a clean, no-issue, exit


def setup_docker_arguments(logger=None):
    # Workspace directories to mount in image are specified.
    volumes_dict = {f"{get_workspace_dir()}": {'bind': f"{get_workspace_dir()}", 'mode': 'rw'}}
    logger.info(f'For image -- mounting volumes: "{volumes_dict}"')

    # Environmental variables to pass into image are specified.
    env_variables = {"BAYOTA_WORKSPACE_HOME": os.environ['BAYOTA_WORKSPACE_HOME']}
    logger.info(f'For image -- environment variables to pass: "{env_variables}"')

    return volumes_dict, env_variables


def read_batch_spec_file(batch_spec_file, logger):
    jeeves = Jeeves()

    batchdict = read_spec(batch_spec_file)

    # Process geographies, and expand any (by matching string pattern) if necessary
    geo_scale = batchdict['geography_scale']
    areas = jeeves.geo.geonames_from_geotypename(geotype=geo_scale)
    strpattern = batchdict['geography_entities']['strmatch']

    if type(strpattern) is list:
        GEOAREAS = []
        for sp in strpattern:
            for item in areas.loc[areas.str.match(sp)].tolist():
                GEOAREAS.append(item)
    else:
        GEOAREAS = areas.loc[areas.str.match(strpattern)].tolist()

    # Get study specification file names
    STUDIES = batchdict['study_specs']

    study_pairs = list(itertools.product(GEOAREAS, STUDIES))

    # read other options
    control_options = batchdict['control_options']

    logger.info('%d %s to be conducted: %s' %
                (len(study_pairs),
                 'study' if len(study_pairs) == 1 else 'studies',
                 study_pairs))

    return geo_scale, study_pairs, control_options


def read_study_control_file(control_file, version):
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
                                                   'mdlspec--' + model_spec_name + '--_geo--' + compact_geo_entity_str + '--.pickle')
    control_dict['model'] = {'spec_file': model_spec_file,
                             'objectiveshortname': model_dict['objectiveshortname'],
                             'constraintshortname': model_dict['constraintshortname'],
                             'saved_file_for_this_study': saved_model_file_for_this_study}

    # Experiments
    experiments = studydict['experiments']
    control_dict['experiments'] = experiments.copy()

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
    one_or_the_other = parser.add_mutually_exclusive_group(required=True)
    one_or_the_other.add_argument("-n", "--batch_spec_name", dest="batch_name", default=None,
                                  help="name for this batch, which should match the batch specification file")
    one_or_the_other.add_argument("-f", "--batch_spec_filepath", dest="batch_spec_filepath", default=None,
                                  help="path for this batch's specification file")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("--log_level", nargs=None, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="change logging level to {debug, info, warning, error, critical}")

    opts = parser.parse_args()

    if not opts.batch_spec_filepath:  # name was specified
        opts.batch_spec_filepath = os.path.join(get_spec_files_dir(), 'batch_study_specs', opts.batch_name + '.yaml')

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    sys.exit(main(opts.batch_spec_filepath,
                  dryrun=opts.dryrun,
                  log_level=opts.log_level))
