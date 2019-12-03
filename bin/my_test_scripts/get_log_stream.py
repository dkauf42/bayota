#!/usr/bin/env python
# get_log_stream.py
# Get aws log streams
# Author: DKaufman

# To get the text of a log using the logstream ID, use:
#   >> aws logs get-log-events --log-group-name /aws/batch/job --log-stream-name Modeling-Bayota/default/b9c15a9d-f26b-4c3b-8516-6eb3f39bb02c --output text

import sys
import argparse
import boto3

client = boto3.client('logs')


def main(logstreamname):
    response = client.get_log_events(
            logGroupName='/aws/batch/job',
            logStreamName=logstreamname)

    print(response)


def parse_cli_arguments():
    """ Input arguments are parsed. """
    parser = argparse.ArgumentParser(description='get some logs.')

    parser.add_argument('logstreamname', metavar='NAME', type=str,
                        help='logstream names for which to get the text')

    return parser.parse_args()


if __name__ == '__main__':
    opt = parse_cli_arguments()

    sys.exit(main(opt.logstreamname))
