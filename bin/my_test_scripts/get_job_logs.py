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


def main(jobid, verbose=False):
    response = client.describe_jobs(jobs=jobid)
    print("jobid | status | jobname")
    for job in response['jobs']:
        print(f"{job['jobId']} | {job['status']:<9} | {job['jobName']}")
        for attempt in job['attempts']:
            if 'exitCode' in attempt['container']:
                exitcode = attempt['container']['exitCode']
            else:
                exitcode = 'NA'
            print(f"  exitcode: {exitcode:<2} | logstream: {attempt['container']['logStreamName']}")
            if verbose and ('reason' in attempt['container']):
                print(f"    reason: {attempt['container']['reason']}")


def parse_cli_arguments():
    """ Input arguments are parsed. """
    parser = argparse.ArgumentParser(description='get some logs.')

    parser.add_argument('-v', '--verbose', action = 'store_true',
                        help='modify output verbosity') 
    parser.add_argument('jobid', metavar='ID', type=str, nargs='+',
                        help='a job for which to get its logstream ids')

    return parser.parse_args()


if __name__ == '__main__':
    opt = parse_cli_arguments()

    sys.exit(main(opt.jobid, verbose=opt.verbose))
