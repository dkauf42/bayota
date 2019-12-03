#!/usr/bin/env python
"""
This submits Docker CMDs to launch the model generation, experiments, and trials.

(This takes the place of:
  - run_step0_batch_of_studies.py
  - run_step1_single_study.py
  - and part of run_step3_conductexperiment.py)

Example usage command:
  >> ./bin/docker_run_scripts/batch_job_runner.py --dryrun -cf ./bin/study_specs/batch_study_specs/maryland_counties.yaml

# Daniel Kaufman, Chesapeake Research Consortium, Inc.
# 23 August 2019
================================================================================
"""

import os
import sys
import boto3
import docker
import datetime
import subprocess
from argparse import ArgumentParser

from bayota_util.spec_and_control_handler import read_spec, notdry, parse_batch_spec, \
    read_study_control_file, read_expcon_file, write_control_with_uniqueid
from bayota_settings.base import get_bayota_version, get_workspace_dir, get_s3workspace_dir, \
    get_docker_image_name, get_spec_files_dir, get_control_dir
from bayota_settings.log_setup import root_logger_setup

from bayota_util.s3_operations import S3ops
batch = boto3.client('batch', region_name='us-east-1')

docker_client = docker.from_env()
docker_image = get_docker_image_name()


def main(batch_spec_file, dryrun=False, no_s3=False, no_docker=False, log_level='INFO') -> int:
    logger = root_logger_setup(consolehandlerlevel=log_level, filehandlerlevel='DEBUG')
    logger.debug(locals())

    version = get_bayota_version()
    logger.info('v----------------------------------------------v')
    logger.info(' ******* %s *******' % ('BayOTA version ' + version).center(30, ' '))
    logger.info(' ************** Batch of studies **************')
    logger.info(f" docker image: '{docker_image}' ")
    logger.info('^----------------------------------------------^')

    # Script locations in the docker image
    if no_docker:
        model_generator_script = '${BAYOTA_HOME}/bin/slurm_scripts/run_step2_generatemodel.py'
        modify_model_script = '${BAYOTA_HOME}/bin/slurm_scripts/run_step3b_modifymodel.py'
        solve_trial_script = '${BAYOTA_HOME}/bin/slurm_scripts/run_step4_solveonetrial.py'
    else:
        model_generator_script = '/root/bayota/bin/slurm_scripts/run_step2_generatemodel.py'
        modify_model_script = '/root/bayota/bin/slurm_scripts/run_step3b_modifymodel.py'
        solve_trial_script = '/root/bayota/bin/slurm_scripts/run_step4_solveonetrial.py'

    """ Batch specification file is read. """
    geo_scale, study_pairs, control_options = parse_batch_spec(batch_spec_file, logger=logger)
    # From the batch spec, we retrieve:
    #     - list of study pairs, i.e. a list of tuples with (geo, model_form_dict)
    #     - control options (a dictionary)

    """ Config and Specification file directories are copied to S3 """
    # Relative path (for specification files)
    common_path = os.path.commonpath([get_workspace_dir(), get_spec_files_dir()])
    relative_path_for_specfiles_dir = os.path.relpath(get_spec_files_dir(), common_path)
    s3_specfiles_dir = get_s3workspace_dir() + '/' + relative_path_for_specfiles_dir + '/'
    # Relative path (for control files)
    common_path = os.path.commonpath([get_workspace_dir(), get_control_dir()])
    relative_path_for_control_dir = os.path.relpath(get_control_dir(), common_path)
    s3_control_dir = get_s3workspace_dir() + '/' + relative_path_for_control_dir + '/'

    s3ops = None
    if not no_s3:
        try:
            s3ops = S3ops(bucketname='modeling-data.chesapeakebay.net', log_level=log_level)
        except EnvironmentError as e:
            logger.info(e)
            logger.info('trying again')
            try:
                s3ops = S3ops(bucketname='modeling-data.chesapeakebay.net', log_level=log_level)
            except EnvironmentError as e:
                logger.error(e)
                raise e
        # Specification files are copied.
        logger.info(f"copying specification files from {get_spec_files_dir()} to the s3 location: {s3_specfiles_dir}")
        s3ops.move_to_s3(local_path=get_spec_files_dir(),
                         destination_path=f"{s3_specfiles_dir}",
                         move_directory=True)
    else:
        logger.info(f"would copy local specification files from {get_spec_files_dir()} to the s3 location: {s3_specfiles_dir}")

    """ Each study (geography, model form) is iterated over. """
    jobids = dict()
    jobids['study'] = dict()
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
        studycon_name = write_control_with_uniqueid(control_dict=control_dict, control_name_prefix='step1_studycon')

        # The local study control file is read....
        experiments, \
        baseloadingfilename, \
        control_dict, \
        geography_name, \
        compact_geo_entity_str, \
        model_spec_name, \
        studyshortname, \
        studyid = read_study_control_file(studycon_name)

        logger.info('v----------------------------------------------v')
        logger.info(' *************** Single Study *****************')
        logger.info(f" Geography = {geography_name}")
        logger.info(f" Model specification name = {model_spec_name}")
        logger.info(f" Experiments = {experiments}")
        logger.info(f" Base_loading_file_name = {baseloadingfilename}")
        logger.info('^----------------------------------------------^')
        move_controlfile_to_s3(logger, no_s3, s3_control_dir, s3ops, controlfile_name=studycon_name)

        """ GENERATE MODEL VIA DOCKER IMAGE """
        # A command is built for this job submission.
        # CMD = f"{model_generator_script} -cn {studycon_name} --s3workspace {get_s3workspace_dir()} --log_level={log_level}"
        # my_run_command(CMD, dryrun, logger, no_docker)

        # To use AWS Batch, we submit the job with a job definition/queue specified.
        response = batch.submit_job(jobName=f"BAYOTA_modelgeneration_using_{studycon_name}",
                                    jobQueue='Modeling',
                                    jobDefinition='Modeling-Bayota:6',
                                    containerOverrides={
                                            "command": ['python',
                                                        model_generator_script,
                                                        '-cn', studycon_name,
                                                        '--s3workspace', get_s3workspace_dir(),
                                                        f"--log_level={log_level}"],
                                    })
        print("Job ID is {}.".format(response['jobId']))
        jobids['study'][studyid] = dict()
        jobids['study'][studyid]['self'] = response['jobId']
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
        # A job is submitted for each experiment in the list.
        p_list = []
        jobids['study'][studyid]['exp'] = dict()
        for ii, exp_spec_name in enumerate(experiments):
            expactiondict = read_spec(spec_file_name=exp_spec_name, spectype='experiment')
            expid = '{:04}'.format(ii + 1)
            logger.info(f"Exp. #{expid}: {exp_spec_name}")

            # "EXPCON": An experiment control file w/unique identifier (uuid4) is written by adding to studycon file.
            try:
                del control_dict["experiments"]
            except KeyError:
                logger.info("Key 'experiments' not found")
            expactiondict['id'] = expid
            control_dict['experiment'] = expactiondict
            control_dict['experiment_name'] = exp_spec_name
            expcon_name = write_control_with_uniqueid(control_dict=control_dict, control_name_prefix='step3_expcon')

            # The local experiment control file is read....
            actionlist, \
            compact_geo_entity_str, \
            control_dict, \
            expid, \
            expname, \
            list_of_trialdicts, \
            saved_model_file, \
            studyid = read_expcon_file(expcon_name)

            logger.info('v--------------------------------------------v')
            logger.info(' ************* Model Modification ***********')
            logger.info('^--------------------------------------------^')
            move_controlfile_to_s3(logger, no_s3, s3_control_dir, s3ops, controlfile_name=expcon_name)

            """ MODIFY MODEL VIA DOCKER IMAGE """
            # CMD = f"{modify_model_script} -cn {expcon_name} --s3workspace {get_s3workspace_dir()} --log_level={log_level}"
            # my_run_command(CMD, dryrun, logger, no_docker)
            # To use AWS Batch, we submit the job with a job definition/queue specified.
            response = batch.submit_job(jobName=f"Bayota_modelmods_using_{expcon_name}",
                                        jobQueue='Modeling',
                                        jobDefinition='Modeling-Bayota:6',
                                        dependsOn=[{'jobId': jobids['study'][studyid]['self'],
                                                    'type': 'N_TO_N'}],
                                        containerOverrides={
                                                "command": ['python',
                                                            modify_model_script,
                                                            '-cn', expcon_name,
                                                            '--s3workspace', get_s3workspace_dir(),
                                                            f"--log_level={log_level}"],
                                        })
            print("Job ID is {}.".format(response['jobId']))
            jobids['study'][studyid]['exp'][expid] = dict()
            jobids['study'][studyid]['exp'][expid]['self'] = response['jobId']

            """ Each trial is iterated over. """
            # List of trial sets to be conducted for this experiment are logged.
            tempstr = 'set' if len(list_of_trialdicts) == 1 else 'sets'
            logger.debug(f"** Single Experiment **: {expname} - trial {tempstr} to be conducted: {list_of_trialdicts}")
            trialnum = 0
            p_list = []
            jobids['study'][studyid]['exp'][expid]['trial'] = dict()
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
                    trialcon_name = write_control_with_uniqueid(control_dict=control_dict,
                                                                control_name_prefix='step4_trialcon')
                    move_controlfile_to_s3(logger, no_s3, s3_control_dir, s3ops, controlfile_name=trialcon_name)

                    """ SOLVE TRIAL VIA DOCKER IMAGE """
                    # CMD = f"{solve_trial_script} -cn {trialcon_name} --s3workspace {get_s3workspace_dir()} --log_level={log_level}"
                    # my_run_command(CMD, dryrun, logger, no_docker)
                    response = batch.submit_job(jobName=f"Bayota_solvetrial_using_{trialcon_name}",
                                                jobQueue='Modeling',
                                                jobDefinition='Modeling-Bayota:6',
                                                dependsOn=[{'jobId': jobids['study'][studyid]['exp'][expid]['self'],
                                                            'type': 'N_TO_N'}],
                                                containerOverrides={
                                                        "command": ['python',
                                                                    solve_trial_script,
                                                                    '-cn', trialcon_name,
                                                                    '--s3workspace', get_s3workspace_dir(),
                                                                    f"--log_level={log_level}"],
                                                })
                    print("Job ID is {}.".format(response['jobId']))
                    jobids['study'][studyid]['exp'][expid]['trial'][trialidstr] = dict()
                    jobids['study'][studyid]['exp'][expid]['trial'][trialidstr]['self'] = response['jobId']

    print(jobids)

    def myprint(d):
        for k, v in d.items():
            if isinstance(v, dict):
                myprint(v)
            else:
                print(v, end=' ')
    print('jobids all together:')
    print('------------------------------')
    myprint(jobids)
    print('\n------------------------------')
    return 0  # a clean, no-issue, exit


def my_run_command(CMD, dryrun, logger, no_docker):
    logger.info(f'job command is: "{CMD}"')
    # Job is submitted.
    if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
        if no_docker:
            p1 = subprocess.Popen([CMD], shell=True)
            p1.wait()
            return_code = p1.returncode  # Get return code from process
            if p1.returncode != 0:
                logger.error(f"command finished with non-zero code <{return_code}>")
                return 1
        else:
            response = docker_client.containers.run(docker_image, CMD)
            logger.info(f"*command submitted to image <{docker_image}>* - response is <{response}>")
    return 0


def move_controlfile_to_s3(logger, no_s3, s3_control_dir, s3ops, controlfile_name):
    """ The local control file is copied to the S3-based workspace. """
    controlfile_localpath = os.path.join(get_control_dir(), controlfile_name) + '.yaml'
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
    """ Input arguments are parsed. """
    parser = ArgumentParser()
    parser.add_argument("-n", "--batch_spec_name", dest="batch_spec_name", required=True,
                        help="name for this batch, which should match the batch specification file")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("--no_s3", action='store_true',
                        help="don't move files to AWS S3 buckets")

    parser.add_argument("--no_docker", action='store_true',
                        help="run through the script locally, without calling a docker image")

    parser.add_argument("--log_level", nargs=None, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="change logging level to {debug, info, warning, error, critical}")

    return parser.parse_args()


if __name__ == '__main__':
    opts = parse_cli_arguments()

    sys.exit(main(opts.batch_spec_name,
                  dryrun=opts.dryrun,
                  no_s3=opts.no_s3,
                  no_docker=opts.no_docker,
                  log_level=opts.log_level))
