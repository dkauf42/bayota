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
#   -lp || --local        = local path of file/dir to move
#   -dp || --destination  = destination directory into which file will be moved (note: no leading or trailing '/'s)
#   -v  || --verbose      = (Optional) print "[In/Out] of AWS" statement
#
# Example:
#   $ ./move_to_s3.py -op local_file -dp s3_folder --verbose
#
##################################################

import os
import sys
import boto3
import requests
from argparse import ArgumentParser


def main(local_path, destination_path, move_directory=False, verbose=False):

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

    s3 = boto3.client('s3')

    if move_directory:
        # enumerate local files recursively
        for root, dirs, files in os.walk(local_path):

            for filename in files:

                # construct the full local path
                local_path = os.path.join(root, filename)

                # construct the full Dropbox path
                relative_path = os.path.relpath(local_path, local_path)
                s3_path = os.path.join(destination_path, relative_path)

                # relative_path = os.path.relpath(os.path.join(root, filename))

                print('Searching "%s" in "%s"' % (s3_path, bucketname))
                try:
                    s3.head_object(Bucket=bucketname, Key=s3_path)
                    print("Path found on S3! Skipping %s..." % s3_path)

                    # try:
                    # client.delete_object(Bucket=bucket, Key=s3_path)
                    # except:
                    # print "Unable to delete %s..." % s3_path
                except:
                    print("Uploading %s..." % s3_path)
                    s3.upload_file(Key=s3_path, Bucket=bucketname, Filename=local_path)
    else:
        # Upload a file
        s3.upload_file(Key=destination_path,  # The name of the key to upload to.
                       Bucket=bucketname,  # The name of the bucket to upload to.
                       Filename=local_path)  # The path to the file to upload.

    return 0  # a clean, no-issue, exit


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()
    # Arguments for top-level
    parser.add_argument("-lp", "--local", dest="local_path", default=None,
                        help="local path of file/dir to move")
    parser.add_argument("-dp", "--destination", dest="destination_path", default=None,
                        help="destination path for files to move")

    parser.add_argument("--dir", dest='move_directory', action='store_true',
                        help="use this flag to move an entire directory, retaining dir structure")

    parser.add_argument("-v", "--verbose", dest='verbose',
                        action="count", default=0)

    opts = parser.parse_args()

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(opts.local_path,
                  opts.destination_path,
                  move_directory=opts.move_directory,
                  verbose=opts.verbose))
