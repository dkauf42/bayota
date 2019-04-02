#!/usr/bin/env python

# Based on https://stackoverflow.com/questions/28634126/aws-s3-through-boto-checking-disk-space
# Since S3 is just a key/value store you need to calculate this manually.
# It doesn't have a concept of a filesystem that you can just query.
# So you'll want to do something like this:

import sys
import boto3
import botocore
import requests
from argparse import ArgumentParser


def main(bucketname='s3://modeling-data.chesapeakebay.net/'):
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
        _S3BUCKET = bucketname
    except:
        print('Not In AWS')
        return 1

    # s3 = boto3.client('s3')  # low-level
    s3 = boto3.resource('s3')  # high-level

    bucket = s3.Bucket(_S3BUCKET)
    if bucket.creation_date:
        print("The bucket exists")
    else:
        print("The bucket does not exist")

    total_bytes = 0
    for key in bucket.objects.all():
       total_bytes += key.size

    print(total_bytes)

    return 0

def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()
    # Arguments for top-level
    parser.add_argument("-b", "--bucket", dest="bucketname", default=None,
                        help="bucket name")

    opts = parser.parse_args()

    print(opts)
    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(bucketname=opts.bucketname))
