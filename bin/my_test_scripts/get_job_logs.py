#!/usr/bin/env python
# get_job_logs.py
# Get aws log streams from a job id
# Author: DKaufman

# To get the text of a log using the logstream ID, use:
#   >> aws logs get-log-events --log-group-name /aws/batch/job --log-stream-name Modeling-Bayota/default/b9c15a9d-f26b-4c3b-8516-6eb3f39bb02c --output text

import sys
import argparse
import boto3

client = boto3.client('batch')


def main(jobid):
    response = client.describe_jobs(jobs=jobid)
    for job in response['jobs']:
        print(f"jobid: {job['jobId']} | jobname: {job['jobName']}")
        print(f"  status: {job['status']}")
        for attempt in job['attempts']:
            print(f"  logstream: {attempt['container']['logStreamName']}")


def parse_cli_arguments():
    """ Input arguments are parsed. """
    parser = argparse.ArgumentParser(description='get some logs.')

    parser.add_argument('jobid', metavar='ID', type=str, nargs='+',
                        help='a job for which to get its logstream ids')

    return parser.parse_args()


if __name__ == '__main__':
    opt = parse_cli_arguments()

    sys.exit(main(opt.jobid))
