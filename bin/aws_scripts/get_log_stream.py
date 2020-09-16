#!/usr/bin/env python
""" Get aws log streams

To get the text of a log using the logstream ID with the AWS CLI, use:
  >> aws logs get-log-events
         --log-group-name /aws/batch/job
         --log-stream-name Modeling-Bayota/default/b9c15a9d-f26b-4c3b-8516-6eb3f39bb02c
         --output text
"""

# Generic/Built-in
import sys
import argparse

# AWS
import boto3
client = boto3.client('logs')


def main(logstreamname, verbose=False):
    response = client.get_log_events(
            logGroupName='/aws/batch/job',
            logStreamName=logstreamname)

    for e in response['events']:
        if not verbose:
            print(e['message'])
        else:
            print(e)
    print(f"nextForwardToken: {response['nextForwardToken']}")
    print(f"nextBackwardToken: {response['nextBackwardToken']}")


def parse_cli_arguments():
    """ Input arguments are parsed. """
    parser = argparse.ArgumentParser(description='get some logs.')

    parser.add_argument('logstreamname', metavar='NAME', type=str,
                        help='logstream names for which to get the text')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="include 'timestamp's and 'ingestionTime's in log events")

    return parser.parse_args()


if __name__ == '__main__':
    opt = parse_cli_arguments()

    sys.exit(main(opt.logstreamname, verbose=opt.verbose))
