#!/usr/bin/env python
# get_job_logs.py
# Get aws log stream and status from job id(s)
# Author: DKaufman
#
# Example usage:
#   ./get_job_logs.py abea20c8-e12e-478c-aa85-bda50679debf d9d4b758-783f-49ab-bc97-1b3b0be83bb6
#
# Can also be used with a pipe, for example with the extract_ids script:
#   ./bin/extract_ids <filename> | ./bin/aws_scripts/get_job_logs.py
#
###CLI Options
# -v || --verbose  = Modify output verbosity to include "reasons" for failed jobs
# -s || --summary  = Only print summary counts of job statuses
#
# Note: To get the text of a log using the logstream ID, use:
#   >> aws logs get-log-events --log-group-name /aws/batch/job --log-stream-name Modeling-Bayota/default/b9c15a9d-f26b-4c3b-8516-6eb3f39bb02c --output text

import sys
import fileinput
import argparse
from collections import Counter

import boto3
client = boto3.client('batch')


def main(jobid, verbose=False, summaryonly=False):
    number_of_jobs = len(jobid)
    status_list = []

    # List of jobs is broken into chunks of 100 so that boto3's describe_jobs() method can handle them.
    jobids_100_at_a_time = [jobid[i:i+100] for i in range(0, number_of_jobs, 100)]

    # A header row is printed first.
    printc("jobid | status | jobname", summaryonly)

    for jobidlist in jobids_100_at_a_time:
        response = client.describe_jobs(jobs=jobidlist)

        for job in response['jobs']:
            jobstatus = job['status']
            status_list.append(jobstatus)

            # Status of job is printed.
            printc(f"{job['jobId']} | {jobstatus:<9} | {job['jobName']}", summaryonly)

            # If job has been attemped, details of each attempt are printed.
            for attempt in job['attempts']:
                if 'exitCode' in attempt['container']:
                    exitcode = attempt['container']['exitCode']
                else:
                    exitcode = 'NA'
                printc(f"  exitcode: {exitcode:<2} | logstream: {attempt['container']['logStreamName']}", summaryonly)
                if verbose and ('reason' in attempt['container']):
                    printc(f"    reason: {attempt['container']['reason']}", summaryonly)

    summary_counts = dict(Counter(status_list))
    print("\n*** Summary of %s jobs (count of each status) ***" % number_of_jobs)
    print('\n'.join("{}: {}".format(k, v) for k, v in sorted(summary_counts.items())))


def printc(msg, /, summaryonly=False):
    """ shorthand conditional print method to reduce extra lines in main() """
    if not summaryonly:
        print(msg)


def parse_cli_arguments():
    """ Input arguments are parsed. """
    parser = argparse.ArgumentParser(description='get some logs.')

    parser.add_argument('jobid', metavar='ID', type=str, nargs='*',
                        help='a job (or list of jobs) for which to get logstream id(s) and status(es)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='modify output verbosity to include "reasons" for failed jobs')
    parser.add_argument('-s', '--summary', action='store_true',
                        help='only print summary counts of job statuses')

    return parser.parse_args()


if __name__ == '__main__':
    opt = parse_cli_arguments()
    
    if len(opt.jobid) < 1:
        strings = sys.stdin.readlines()[0]
        jobid_list = strings.split()
    else:
        jobid_list = opt.jobid    

    sys.exit(main(jobid_list,
                  verbose=opt.verbose,
                  summaryonly=opt.summary))
