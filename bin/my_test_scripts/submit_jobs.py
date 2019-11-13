# job_runner.py: gis cloud test case, 
# Get list of folders, and process each using another python script.
# Author: JMassey 

import sys
import argparse
import boto3
import sys
import os
from timeit import default_timer as timer

batch = boto3.client('batch')

def main():
    # 1 - Define Variables passed from CLI, assign to variables for simplicity
    #parser = argparse.ArgumentParser(description='Merge Raster Images from data stored in s3.')
    #parser.add_argument('bucket', help="Source S3 Bucket location, do not include s3://")
    #parser.add_argument('s3path', help="Path to files to be processed in bucket ex: cloud_test/BlueRidge_DEMs_1")
    #args = parser.parse_args()

    #_BUCKET_NAME = args.bucket
    #_PREFIX = args.s3path + '/'

    #print('S3 Bucket:     %s' % _BUCKET_NAME)
    #print('S3 Bucket Key: %s' % _PREFIX)

    #all_folder_list = list_folders_in_bucket(_BUCKET_NAME, _PREFIX)

    #print ('\nFolders found in: %s' % _PREFIX)
    #for folder in all_folder_list:
        # Submit Jobs to Batch here
    #    print (folder)

    response = batch.submit_job(jobName='Bayota_Testing',
                        jobQueue='Modeling',
                        jobDefinition='Modeling-Bayota:5',
                        containerOverrides={
                            "command": ['python', '/root/bayota/bin/slurm_scripts/run_step2_generatemodel.py', '-cn' , 'step1_studycon1d6c68f6-326c-4487-8d85-5c5113f67bd7' , '--s3workspace', 'optimization/ws_copies/bayota_ws_0.1b2','--log_level=INFO'], 
                        })
    print("Job ID is {}.".format(response['jobId']))

    response2 = batch.submit_job(jobName='Bayota_Testing_step2',
                        jobQueue='Modeling',
                        dependsOn=[
                            {
                                'jobId': response['jobId'],
                                'type': 'N_TO_N'
                            },
                        ],
                        jobDefinition='Modeling-Bayota:5',
                        containerOverrides={
                            "command": ['python', '/root/bayota/bin/slurm_scripts/run_step3b_modifymodel.py', '-cn' , 'step3_expcon70ab6881-1c51-4f03-bcf2-fdef72e5662d' , '--s3workspace','optimization/ws_copies/bayota_ws_0.1b2','--log_level=INFO'], 
                        })
    print("Job ID is {}.".format(response['jobId']))

    response3 = batch.submit_job(jobName='Bayota_Testing_step3',
                        jobQueue='Modeling',
                        dependsOn=[
                            {
                                'jobId': response2['jobId'],
                                'type': 'N_TO_N'
                            },
                        ],
                        jobDefinition='Modeling-Bayota:5',
                        containerOverrides={
                            "command": ['python', '/root/bayota/bin/slurm_scripts/run_step4_solveonetrial.py', '-cn' , 'step4_trialcon2534e7f9-9e4b-4544-b351-4fe231bb4f0a' , '--s3workspace','optimization/ws_copies/bayota_ws_0.1b2','--log_level=INFO'], 
                        })
    print("Job ID is {}.".format(response3['jobId']))

if __name__ == '__main__':
    main()