#!/usr/bin/env python
import os
import sys
import boto3
import requests
import subprocess
from argparse import ArgumentParser


class S3ops():
    def __init__(self, bucketname='modeling-data.chesapeakebay.net', verbose=False):
        # Check if running on AWS
        self.resp = None
        self.bucketname = bucketname
        self.s3 = None

        try:
            resp = requests.get('http://169.254.169.254', timeout=0.001)
            if verbose:
                print('In AWS')
        except:
            raise EnvironmentError('Not In AWS')

        self.s3 = boto3.client('s3')

    def get_from_s3(self, s3path, local_path):
        """ Get files from S3

        Args:
            s3path: s3 path of directory
            local_path: local path to which directory should be moved
            verbose:

        Returns:

        Example:
            >>> S3ops.get_from_s3(s3path='s3://modeling-data/data_dir', local_path='/modeling/local_dir')

        """
        CMD = f"aws s3 sync {s3path} {local_path}"
        subprocess.Popen([CMD], shell=True)

        return 0

    def move_to_s3(self, local_path, destination_path, move_directory=False, verbose=False):
        """ Move files to S3

        Args:
            local_path: local path of file/dir to move
            destination_path: destination directory into which file will be moved (note: no leading or trailing '/'s)
            move_directory: if local path is a directory, will move full directory recursively
            verbose: (Optional) print "[In/Out] of AWS" statement

        Returns:
            0 for a clean, no-error result
            1 for an error

        Example:
            >>> S3ops.move_to_s3('/modeling/local_dir', 's3://modeling-data/data_dir', move_directory=True)

        """
        if move_directory:
            if not os.path.isdir(local_path):
                print('Local directory <%s> does not exist' % local_path)
                return 1

            # enumerate local files recursively
            for root, dirs, files in os.walk(local_path):

                for filename in files:

                    # construct the full local path
                    local_file = os.path.join(root, filename)
                    # construct the full s3 path
                    relative_path = os.path.relpath(local_file, local_path)
                    s3_path = os.path.join(destination_path, relative_path)

                    if verbose:
                        print('Searching "%s" in "%s"' % (s3_path, self.bucketname))
                    try:
                        self.s3.head_object(Bucket=self.bucketname, Key=s3_path)
                        if verbose:
                            print("Path found on S3! Skipping %s..." % s3_path)

                        # try:
                        # client.delete_object(Bucket=bucket, Key=s3_path)
                        # except:
                        # print "Unable to delete %s..." % s3_path
                    except:
                        if verbose:
                            print("Uploading %s..." % s3_path)
                        self.s3.upload_file(Key=s3_path, Bucket=self.bucketname, Filename=local_file)
        else:
            # Upload a file
            self.s3.upload_file(Key=destination_path,  # The name of the key to upload to.
                           Bucket=self.bucketname,  # The name of the bucket to upload to.
                           Filename=local_path)  # The path to the file to upload.

        return 0  # a clean, no-issue, exit

    """ Command Line Interface """

    def cli(self, args):
        # Input arguments are parsed.
        parser = ArgumentParser()
        # Arguments for top-level
        parser.add_argument('command', action="store", type=str, choices=['pull', 'push'])
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        self.response = getattr(self, args.command)()

    def pull(self):
        parser = ArgumentParser(description='Retrieve a file from s3')
        # prefixing the argument with -- means it's optional
        parser.add_argument("s3_path", help="s3 path of directory")
        parser.add_argument("local_path", help="local path to which directory should be moved")
        parser.add_argument("-v", "--verbose", dest='verbose',
                            action="count", default=0)
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (s3_operations) and the subcommand (pull)
        args = parser.parse_args(sys.argv[2:])

        return self.get_from_s3(s3path=args.s3_path, local_path=args.local_path)

    def push(self):
        parser = ArgumentParser(description='Move a file to s3')
        # prefixing the argument with -- means it's optional
        parser.add_argument("local_path", help="local path of file/dir to move")
        parser.add_argument("s3_path", help="destination path for files to move")
        parser.add_argument("--recursive", dest='move_directory', action='store_true',
                            help="use this flag to move an entire directory, retaining dir structure")
        parser.add_argument("-v", "--verbose", dest='verbose',
                            action="count", default=0)
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (s3_operations) and the subcommand (push)
        args = parser.parse_args(sys.argv[2:])

        return self.move_to_s3(local_path=args.local_path,
                               destination_path=args.s3_path,
                               move_directory=args.move_directory,
                               verbose=args.verbose)


if __name__ == '__main__':
    s3ops = S3ops()
    s3ops.cli(sys.argv[:])
