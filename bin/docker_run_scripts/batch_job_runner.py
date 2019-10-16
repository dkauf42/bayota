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
from argparse import ArgumentParser

from bayota_util.spec_handler import read_spec, notdry, read_batch_spec_file, \
    read_study_control_file, read_expcon_file
from bayota_settings.base import get_bayota_version, get_workspace_dir, \
    get_spec_files_dir, get_control_dir, get_experiment_specs_dir
from bayota_settings.log_setup import root_logger_setup

from bayota_util.s3_operations import S3ops
# batch = boto3.client('batch', region_name='us-east-1')

docker_client = docker.from_env()
docker_image = 'bayota_conda_then_ipopt_app'

# Script locations in the docker image
model_generator_script = '/root/bayota/bin/slurm_scripts/run_step2_generatemodel.py'
modify_model_script = '/root/bayota/bin/slurm_scripts/run_step3b_modifymodel.py'
solve_trial_script = '/root/bayota/bin/slurm_scripts/run_step4_solveonetrial.py'


def main(batch_spec_file, dryrun=False, no_s3=False, log_level='INFO') -> int:
    logger = root_logger_setup(consolehandlerlevel=log_level, filehandlerlevel='DEBUG')
    logger.debug(locals())

    version = get_bayota_version()
    logger.info('v----------------------------------------------v')
    logger.info(' ******* %s *******' % ('BayOTA version ' + version).center(30, ' '))
    logger.info(' ************** Batch of studies **************')
    logger.info('^----------------------------------------------^')

    """ Batch specification file is read. """
    geo_scale, study_pairs, control_options = read_batch_spec_file(batch_spec_file, logger=logger)
    # From the batch spec, we retrieve:
    #     - list of study pairs, i.e. a list of tuples with (geo, model_form_dict)
    #     - control options (a dictionary)

    """ Workspace is copied in full to S3 """
    ws_dir_name = os.path.basename(os.path.normpath(get_workspace_dir()))
    s3_ws_base_path = 'optimization/ws_copies/'
    s3_ws_dir = s3_ws_base_path + ws_dir_name
    s3ops = None
    if not no_s3:
        try:
            s3ops = S3ops(verbose=True, bucketname='modeling-data.chesapeakebay.net')
        except EnvironmentError as e:
            logger.info(e)
            logger.info('trying again')
            try:
                s3ops = S3ops(verbose=True, bucketname='modeling-data.chesapeakebay.net')
            except EnvironmentError as e:
                logger.error(e)
                raise e
        # Workspace is copied.
        s3ops.move_to_s3(local_path=get_workspace_dir(),
                         destination_path=f"{s3_ws_dir}",
                         move_directory=True)
        logger.info(f"copied local workspace from {get_workspace_dir()} to the s3 location: {s3_ws_dir}")
    else:
        logger.info(f"would copy local workspace from {get_workspace_dir()} to the s3 location: {s3_ws_dir}")
    common_path = os.path.commonpath([get_workspace_dir(), get_control_dir()])
    relative_path_for_control_dir = os.path.relpath(get_control_dir(), common_path)
    s3_control_dir = s3_ws_dir + '/' + relative_path_for_control_dir + '/'

    """ Each study (geography, model form) is iterated over. """
    for index, sp in enumerate(study_pairs):
        # (ModelGeography, ModelForm+Experiments) are combined to form studies, which are submitted as jobs.

        # Study information is pulled apart.
        geoname = sp[0]  # model geography (first part of the study_pair tuples)
        studyspecdict = sp[1]  # model form + experiment (second part of the study_pair tuples)

        # A name and ID are formed for this study.
        filesafegeostring = geoname.replace(' ', '').replace(',', '')
        studyid = '{:04}'.format(index + 1)
        spname = filesafegeostring + f"_s{studyid}"
        studyspecdict['studyshortname'] = spname
        studyspecdict['id'] = studyid

        # "STUDYCON": A study control file w/unique identifier (uuid4) is created and written locally.
        control_dict = {"geography": {'scale': geo_scale, 'entity': geoname},
                        "study": studyspecdict, "control_options": control_options,
                        "code_version": version,
                        "run_timestamps": {'step0_batch': datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}}
        studycon_name = 'step1_studycon' + str(uuid.uuid4())
        study_control_file = os.path.join(get_control_dir(), studycon_name) + '.yaml'
        with open(study_control_file, "w") as f:
            yaml.safe_dump(control_dict, f, default_flow_style=False)
        # The local study control file is read....
        experiments, \
        baseloadingfilename, \
        control_dict, \
        geography_name, \
        compact_geo_entity_str, \
        model_spec_name, \
        studyshortname, \
        studyid = read_study_control_file(study_control_file, version)

        logger.info('v----------------------------------------------v')
        logger.info(' *************** Single Study *****************')
        logger.info(f" Geography = {geography_name}")
        logger.info(f" Model specification name = {model_spec_name}")
        logger.info(f" Experiments = {experiments}")
        logger.info(f" Base_loading_file_name = {baseloadingfilename}")
        logger.info('^----------------------------------------------^')
        move_controlfile_to_s3(logger, no_s3, s3_control_dir, s3ops,
                               controlfile_localpath=study_control_file, controlfile_name=studycon_name)

        """ GENERATE MODEL VIA DOCKER IMAGE """
        env_variables = setup_docker_arguments(logger=logger)
        # A command is built for this job submission.
        CMD = f"{model_generator_script} -cn {studycon_name} --s3workspace {s3_ws_dir} --log_level={log_level}"
        logger.info(f'For image -- job command is: "{CMD}"')
        # Job is submitted.
        if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
            response = docker_client.containers.run(docker_image, CMD, environment=env_variables)
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

        """ Each experiment is iterated over. """
        env_variables = setup_docker_arguments(logger=logger)
        # A job is submitted for each experiment in the list.
        p_list = []
        for ii, exp in enumerate(experiments):
            expspec_file = os.path.join(get_experiment_specs_dir(), exp)
            expactiondict = read_spec(expspec_file + '.yaml')
            expid = '{:04}'.format(ii + 1)
            logger.info(f"Exp. #{expid}: {exp}")

            # "EXPCON": An experiment control file w/unique identifier (uuid4) is written by adding to studycon file.
            try:
                del control_dict["experiments"]
            except KeyError:
                logger.info("Key 'experiments' not found")
            expactiondict['id'] = expid
            control_dict['experiment'] = expactiondict
            control_dict['experiment_file'] = expspec_file
            expcon_name = 'step3_expcon' + str(uuid.uuid4())
            exp_control_file = os.path.join(get_control_dir(), expcon_name) + '.yaml'
            with open(exp_control_file, "w") as f:
                yaml.safe_dump(control_dict, f, default_flow_style=False)
            # The local experiment control file is read....
            actionlist, \
            compact_geo_entity_str, \
            control_dict, \
            expid, \
            expname, \
            list_of_trialdicts, \
            saved_model_file, \
            studyid = read_expcon_file(exp_control_file)

            logger.info('v--------------------------------------------v')
            logger.info(' ************* Model Modification ***********')
            logger.info('^--------------------------------------------^')
            move_controlfile_to_s3(logger, no_s3, s3_control_dir, s3ops,
                                   controlfile_localpath=exp_control_file, controlfile_name=expcon_name)

            CMD = f"{modify_model_script} -cn {expcon_name} --s3workspace {s3_ws_dir} --log_level={log_level}"
            logger.info(f'For image -- job command is: "{CMD}"')
            # Job is submitted.
            if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
                response = docker_client.containers.run(docker_image, CMD, environment=env_variables)
                logger.info(f"*command submitted to image <{docker_image}>* - response is <{response}>")

            """ Each trial is iterated over. """
            # List of trial sets to be conducted for this experiment are logged.
            tempstr = 'set' if len(list_of_trialdicts) == 1 else 'sets'
            logger.debug(f"** Single Experiment **: {expname} - trial {tempstr} to be conducted: {list_of_trialdicts}")
            trialnum = 0
            p_list = []
            for i, dictwithtrials in enumerate(list_of_trialdicts):
                logger.info('v--------------------------------------------v')
                logger.info(' **************** Trial Set *****************')
                logger.info(f" Geography = {compact_geo_entity_str}")
                logger.info(f" Experiment = {expname}")
                logger.info(f" Set #{i}: = {dictwithtrials}")
                logger.info('^--------------------------------------------^')

                # Variable value(s) for this trial set are parsed.
                modvar = dictwithtrials['variable']
                varvalue = dictwithtrials['value']
                logger.debug(f'variable to modify: {modvar}')
                logger.debug('values: %s' % varvalue)
                varindexer = None
                try:
                    varindexer = dictwithtrials['indexer']
                    logger.debug(f'indexed over: {varindexer}')
                except KeyError:
                    pass

                # Loop through and start each trial
                for vi in varvalue:
                    trialnum += 1
                    trialidstr = '{:04}'.format(trialnum)
                    modificationstr = f"\'{{\"variable\": \"{modvar}\", " \
                                      f"\"value\": {vi}, " \
                                      f"\"indexer\": \"{varindexer}\"}}\'"
                    logger.info(f'trial #{trialidstr}, setting <{modvar}> to <{vi}>')

                    # "TRIALCON": A trial control file w/unique identifier (uuid4) is written by adding to expcon file.
                    control_dict['trial'] = {'id': trialidstr,
                                             'trial_name': 'exp--' + expname + '--_modvar--' + modvar + '--_trial' + trialidstr,
                                             'modification': modificationstr,
                                             'solutions_folder_name': expname}
                    control_dict['code_version']: version
                    control_dict['run_timestamps']['step4_trial'] = datetime.datetime.today().strftime(
                        '%Y-%m-%d-%H:%M:%S')
                    trialcon_name = 'step4_trialcon' + str(uuid.uuid4())
                    trial_control_file = os.path.join(get_control_dir(), trialcon_name) + '.yaml'
                    with open(trial_control_file, "w") as f:
                        yaml.safe_dump(control_dict, f, default_flow_style=False)

                    move_controlfile_to_s3(logger, no_s3, s3_control_dir, s3ops,
                                           controlfile_localpath=trial_control_file, controlfile_name=trialcon_name)

                    """ SOLVE TRIAL VIA DOCKER IMAGE """
                    CMD = f"{solve_trial_script} -cn {trialcon_name} --s3workspace {s3_ws_dir} --log_level={log_level}"
                    logger.info(f'For image -- job command is: "{CMD}"')
                    # Job is submitted.
                    if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
                        response = docker_client.containers.run(docker_image, CMD, environment=env_variables)
                        logger.info(f"*command submitted to image <{docker_image}>* - response is <{response}>")

    return 0  # a clean, no-issue, exit


def move_controlfile_to_s3(logger, no_s3, s3_control_dir, s3ops, controlfile_localpath, controlfile_name):
    # The local control file is copied to the S3-based workspace.
    controlfile_s3path = s3_control_dir + controlfile_name + '.yaml'
    if not no_s3:
        s3ops.move_to_s3(local_path=controlfile_localpath, destination_path=f"{controlfile_s3path}")
    else:
        logger.info(f"would copy control file to {controlfile_s3path}")


def setup_docker_arguments(logger=None):
    # Workspace directories to mount in image are specified.
    # volumes_dict = {f"{get_workspace_dir()}": {'bind': f"{get_workspace_dir()}", 'mode': 'rw'}}
    # logger.info(f'For image -- mounting volumes: "{volumes_dict}"')

    # Environmental variables to pass into image are specified.
    env_variables = {"BAYOTA_WORKSPACE_HOME": os.environ['BAYOTA_WORKSPACE_HOME']}
    logger.debug(f'For image -- environment variables to pass: "{env_variables}"')

    return env_variables


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

    parser.add_argument("--no_s3", action='store_true')

    opts = parser.parse_args()

    if not opts.batch_spec_filepath:  # name was specified
        opts.batch_spec_filepath = os.path.join(get_spec_files_dir(), 'batch_study_specs', opts.batch_name + '.yaml')

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    sys.exit(main(opts.batch_spec_filepath,
                  dryrun=opts.dryrun,
                  no_s3=opts.no_s3,
                  log_level=opts.log_level))
