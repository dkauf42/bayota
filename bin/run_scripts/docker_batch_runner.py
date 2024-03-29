#!/usr/bin/env python
""" This submits Docker CMDs to launch the model generation, experiments, and trials.

(This takes the place of:
  - slurm_batch_runner.py
  - slurm_batch_subrunner1_study.py
  - and part of slurm_batch_subrunner2_experiment.py)

It calls the following subordinate scripts to be run in the docker container:
A model_generator_script: "step1_generatemodel.py"
A modify_model_script: "step2_modifymodel.py"
A solve_trial_script: "step3_solveonetrial.py"

Example usage command:
  >> ./bin/run_scripts/docker_batch_runner.py --dryrun maryland_counties

# Daniel Kaufman, Chesapeake Research Consortium, Inc.
# 23 August 2019
================================================================================
"""

# Generic/Built-in
import os
import sys
import time
import datetime
import subprocess
from argparse import ArgumentParser

# BAYOTA
from bayota_util.spec_and_control_handler import read_spec, notdry, parse_batch_spec, \
    read_study_control_file, read_expcon_file, write_control_with_uniqueid
from bayota_settings.base import get_bayota_version, get_docker_image_name, get_spec_files_dir
from bayota_settings.log_setup import root_logger_setup
from bayota_util.s3_operations import move_controlfile_to_s3, establish_s3_connection

# AWS
import boto3
batch = boto3.client('batch', region_name='us-east-1')

# Docker
import docker
docker_client = docker.from_env()
docker_image = get_docker_image_name()


def main(batch_spec_file, dryrun=False, no_s3=False, no_docker=False, log_level='INFO') -> int:
    starttime = time.time()

    # Logging formats are set up.
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
        model_generator_script = '${BAYOTA_HOME}/bin/run_steps/step1_generatemodel.py'
        modify_model_script = '${BAYOTA_HOME}/bin/run_steps/step2_modifymodel.py'
        solve_trial_script = '${BAYOTA_HOME}/bin/run_steps/step3_solveonetrial.py'
    else:
        model_generator_script = '/root/bayota/bin/run_steps/step1_generatemodel.py'
        modify_model_script = '/root/bayota/bin/run_steps/step2_modifymodel.py'
        solve_trial_script = '/root/bayota/bin/run_steps/step3_solveonetrial.py'

    """ Batch specification file is read. """
    geo_scale, study_pairs, control_options = parse_batch_spec(batch_spec_file, logger=logger)
    # From the batch spec, we retrieve:
    #     - list of study pairs, i.e. a list of tuples with (geo, model_form_dict)
    #     - control options (a dictionary)

    """ Specification files are moved to s3. """
    s3ops = None
    local_specfiles_path = get_spec_files_dir(s3=False)
    s3_specfiles_path = get_spec_files_dir(s3=True)
    if not no_s3:
        s3ops = establish_s3_connection(log_level, logger)
        logger.info(f"copying specification files from {local_specfiles_path} to the s3 location: {s3_specfiles_path}")
        s3ops.move_to_s3(local_path=local_specfiles_path,
                         destination_path=s3_specfiles_path,
                         move_directory=True)
    else:
        logger.info(f"would copy local specification files from {local_specfiles_path} to the s3 location: {s3_specfiles_path}")

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
                        "code_version": version}
        studycon_name = write_control_with_uniqueid(control_dict=control_dict, name_prefix='step1_studycon',
                                                    logger=logger)

        # The local study control file is read....
        control_dict, \
        experiments, \
        baseloadingfilename, \
        geography_name, \
        compact_geo_entity_str, \
        model_spec_name, \
        studyshortname, \
        studyid = read_study_control_file(studycon_name)
        move_controlfile_to_s3(logger, s3ops, controlfile_name=studycon_name, no_s3=no_s3)

        logger.info('v----------------------------------------------v')
        logger.info(' *************** Single Study *****************')
        logger.info(f" Geography = {geography_name}")
        logger.info(f" Model specification name = {model_spec_name}")
        logger.info(f" Experiments = {experiments}")
        logger.info(f" Base_loading_file_name = {baseloadingfilename}")
        logger.info('^----------------------------------------------^')
        logger.info('')
        logger.info('v--------------------------------------------v')
        logger.info(' ************** Model Generation ************')
        logger.info('^--------------------------------------------^')

        """ GENERATE MODEL VIA DOCKER IMAGE """
        # Job is submitted to AWS Batch.
        CMD = ['python', model_generator_script, studycon_name,
               '--use_s3_ws',  '--save_to_s3', f"--log_level={log_level}"]
        response = batch.submit_job(jobName=f"BAYOTA_modelgeneration_using_{studycon_name}",
                                    jobQueue='Modeling',
                                    jobDefinition='Modeling-Bayota:6',
                                    containerOverrides={"command": CMD},
                                    retryStrategy={'attempts': 2}
                                    )
        print(f"submitted command: {CMD}")
        print("Job ID is {}.".format(response['jobId']))
        jobids['study'][studyid] = dict()
        jobids['study'][studyid]['self'] = response['jobId']

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
            control_dict['experiment']['uuid'] = control_dict['study']['uuid'] + '_e' + expid
            expcon_name = write_control_with_uniqueid(control_dict=control_dict, name_prefix='step3_expcon',
                                                      logger=logger)

            # The local experiment control file is read....
            control_dict, \
            actionlist, \
            compact_geo_entity_str, \
            expid, \
            expname, \
            list_of_trialdicts, \
            saved_model_file, \
            studyid = read_expcon_file(expcon_name)

            logger.info('v--------------------------------------------v')
            logger.info(' ************* Model Modification ***********')
            logger.info('^--------------------------------------------^')
            move_controlfile_to_s3(logger, s3ops, controlfile_name=expcon_name, no_s3=no_s3)

            """ MODIFY MODEL VIA DOCKER IMAGE """
            # Job is submitted to AWS Batch.
            CMD = ['python', modify_model_script, expcon_name,
                   '--use_s3_ws', '--save_to_s3', f"--log_level={log_level}"]
            response = batch.submit_job(jobName=f"Bayota_modelmods_using_{expcon_name}",
                                        jobQueue='Modeling',
                                        jobDefinition='Modeling-Bayota:6',
                                        dependsOn=[{'jobId': jobids['study'][studyid]['self']}],
                                        containerOverrides={"command": CMD},
                                        retryStrategy={'attempts': 2}
                                        )
            print(f"submitted command: {CMD}")
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
                    control_dict['trial']['uuid'] = control_dict['experiment']['uuid'] + '_t' + trialidstr
                    control_dict['code_version']: version
                    control_dict['submission_timestamps']['step4_trial'] = datetime.datetime.today().strftime(
                        '%Y-%m-%d-%H:%M:%S')
                    trialcon_name = write_control_with_uniqueid(control_dict=control_dict, name_prefix='step4_trialcon',
                                                                logger=logger)
                    move_controlfile_to_s3(logger, s3ops, controlfile_name=trialcon_name, no_s3=no_s3)

                    """ SOLVE TRIAL VIA DOCKER IMAGE """
                    # Job is submitted to AWS Batch.
                    CMD = ['python', solve_trial_script, trialcon_name,
                           '--use_s3_ws', '--save_to_s3', f"--log_level={log_level}"]
                    response = batch.submit_job(jobName=f"Bayota_solvetrial_using_{trialcon_name}",
                                                jobQueue='Modeling',
                                                jobDefinition='Modeling-Bayota:6',
                                                dependsOn=[{'jobId': jobids['study'][studyid]['exp'][expid]['self']}],
                                                containerOverrides={"command": CMD},
                                                retryStrategy={'attempts': 10},
                                                timeout={'attemptDurationSeconds': 3600}
                                                )
                    print(f"submitted command: {CMD}")
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
    print('jobids=', end='')  # Note: this "jobids=" string is used as a key when extracting jobids from a file.
    myprint(jobids)
    print('\n------------------------------')

    endtime = time.time()
    print(f"time elapsed (seconds) since starting the batch_job_runner: {endtime - starttime}")

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
    parser = ArgumentParser(description="Run a batch of optimization studies")

    parser.add_argument('batch_spec_name', metavar='Batch Name', type=str,
                        help='name for this batch, which should match the batch specification file')

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
