#!/usr/bin/env python

import sys
import boto3
import requests
from argparse import ArgumentParser

# Check if running on AWS
inaws = False
# s3 = None
_S3BUCKET = ''
try:
    resp = requests.get('http://169.254.169.254', timeout=0.001)
    print('In AWS')
    inaws = True

    # import s3fs
    # s3 = s3fs.core.S3FileSystem(anon=False)
    _S3BUCKET = 's3://modeling-data.chesapeakebay.net/'
except:
    print('Not In AWS')


def main(original_path, destination_path):

    s3 = boto3.client('s3')
    s3.upload_file(Key=destination_path,  # The name of the key to upload to.
                   Bucket='modeling-data.chesapeakebay.net',  # The name of the bucket to upload to.
                   Filename=original_path)  # The path to the file to upload.


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()
    # Arguments for top-level
    parser.add_argument("-op", "--original", dest="original_path", default=None,
                        help="original path for files to move")
    parser.add_argument("-dp", "--destination", dest="destination_path", default=None,
                        help="destination path for files to move")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("-v", "--verbose", dest='verbose',
                        action="count", default=0)

    opts = parser.parse_args()

    print(opts)
    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(opts.original_path,
                  opts.destination_path))