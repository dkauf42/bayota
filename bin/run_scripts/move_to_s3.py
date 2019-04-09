#!/usr/bin/env python

#
# Example:
#   $ move_to_s3.py --verbose

##################################################
# Danny Kaufman
# 2019 April 09
#
# Move files to S3
#
# Arguments:
#   -op || --original     = original path for file to move
#   -dp || --destination  = destination directory into which file will be moved (note: no leading or trailing '/'s)
#   -v  || --verbose      = (Optional) print "[In/Out] of AWS" statement
#
# Example:
#   $ ./move_to_s3.py -op solution.csv -dp toplevels3dir/solutions_folder --verbose
#
##################################################

import sys
import boto3
import requests
from argparse import ArgumentParser


def main(original_path, destination_path, verbose=False):

    # Check if running on AWS
    try:
        resp = requests.get('http://169.254.169.254', timeout=0.001)
        bucketname = 'modeling-data.chesapeakebay.net'
        if verbose:
            print('In AWS')
    except:
        if verbose:
            print('Not In AWS')
        return 1  # exit with an error

    # Upload a file
    s3 = boto3.client('s3')
    s3.upload_file(Key=destination_path,  # The name of the key to upload to.
                   Bucket=bucketname,  # The name of the bucket to upload to.
                   Filename=original_path)  # The path to the file to upload.

    return 0  # a clean, no-issue, exit


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()
    # Arguments for top-level
    parser.add_argument("-op", "--original", dest="original_path", default=None,
                        help="original path for files to move")
    parser.add_argument("-dp", "--destination", dest="destination_path", default=None,
                        help="destination path for files to move")

    parser.add_argument("-v", "--verbose", dest='verbose',
                        action="count", default=0)

    opts = parser.parse_args()

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(opts.original_path,
                  opts.destination_path,
                  verbose=opts.verbose))
