#!/usr/bin/env python

##################################################
# Danny Kaufman
# 2019 April 12
#
# Get files from S3
#
# Arguments:
#   --from            = s3 path of directory
#   -l || --local     = local path to which directory should be moved
#   -m || --mode      = [cp || sync]
#   -v  || --verbose  = (Optional)
#
# Example:
#   $ ./get_from_s3.py --from s3://modeling-data/data_dir -l /modeling/local_dir --verbose
#
##################################################

import sys
import subprocess
from argparse import ArgumentParser

def main(s3path, local_path, verbose):
    CMD = f"aws s3 sync {s3path} {local_path}"
    subprocess.Popen([CMD], shell=True)

    return 0

def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()
    # Arguments for top-level
    parser.add_argument("--from", dest="s3path", default=None,
                        help="s3 path of directory")
    parser.add_argument("-l", "--local", dest="local_path", default=None,
                        help="local path to which directory should be moved")
    
    parser.add_argument("-m", "--mode", dest="mode", default='sync',
                        choices=['cp', 'sync'], help="copy or sync")

    parser.add_argument("-v", "--verbose", dest='verbose',
                        action="count", default=0)

    opts = parser.parse_args()

    return opts

if __name__ == '__main__':
    opts = parse_cli_arguments()
    
    sys.exit(main(opts.s3path,
                  opts.local_path,
                  verbose=opts.verbose))
