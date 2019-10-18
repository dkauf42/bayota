#!/usr/bin/env python
##################################################
# Danny Kaufman
# 2019 Aug 27
#
# Move files between S3 and local
#
# Command
#   {push, pull}
#
# [pull] Arguments:
#   s3_path           = s3 path of file/directory
#   local_path        = local path to which file/directory should be moved
#   -r || --recursive = if target is a directory, this flag is required
#
# [push] Arguments:
#   local_path        = local path of file/directory
#   s3_path           = s3 path to which file/directory should be moved
#   -r || --recursive = if target is a directory, this flag is required
#
# Example:
#   $ ./s3_oeprations.py pull --recursive s3://modeling-data/data_dir -l /modeling/local_dir
#
##################################################
import os
import sys
import boto3
import botocore
import requests
import subprocess
from argparse import ArgumentParser

from bayota_settings.base import get_workspace_dir
from bayota_settings.log_setup import set_up_detailedfilelogger


class S3ops:
    def __init__(self, bucketname='modeling-data.chesapeakebay.net', log_level='INFO'):
        """

        Args:
            bucketname:
            verbose:
        """
        self.logger = set_up_detailedfilelogger(loggername='s3_operations',  # same name as module, so logger is shared
                                                filename=f"s3ops.log",
                                                level=log_level,
                                                also_logtoconsole=True,
                                                add_filehandler_if_already_exists=True,
                                                add_consolehandler_if_already_exists=False)

        # Check if running on AWS
        self.resp = None
        self.bucketname = bucketname
        self.s3 = None

        try:
            resp = requests.get('http://169.254.169.254', timeout=0.001)
            self.logger.info('In AWS')
        except:
            raise EnvironmentError('Not In AWS')

        self.s3 = boto3.client('s3')

    def get_from_s3(self, s3path, local_path, move_directory=False):
        """ Get files from S3

        Args:
            s3path: s3 path of directory (not including s3://<bucket_name>)
            local_path: local path to which directory should be moved
            verbose:

        Returns:

        Example:
            >>> S3ops.get_from_s3(s3path='data_dir/subfolder', local_path='/modeling/local_dir')

        """
        if move_directory:
            CMD = f"aws s3 sync s3://{self.bucketname}/{s3path} {local_path}"
        else:
            CMD = f"aws s3 cp s3://{self.bucketname}/{s3path} {local_path}"

        self.logger.info(f"submitting command: {CMD}")
        p1 = subprocess.Popen([CMD], shell=True)
        p1.wait()
        # Get return code from process
        return_code = p1.returncode
        if p1.returncode != 0:
            print(f"ERROR: get_from_s3 finished with non-zero code <{return_code}>")
            return 1

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
                self.logger.info('Local directory <%s> does not exist' % local_path)
                return 1

            # enumerate local files recursively
            for root, dirs, files in os.walk(local_path):

                for filename in files:

                    # construct the full local path
                    local_file = os.path.join(root, filename)
                    # construct the full s3 path
                    relative_path = os.path.relpath(local_file, local_path)
                    s3_path = os.path.join(destination_path, relative_path)

                    self.logger.debug('Searching "%s" in "%s"' % (s3_path, self.bucketname))
                    try:
                        self.s3.head_object(Bucket=self.bucketname, Key=s3_path)
                        self.logger.debug("Path found on S3! Skipping %s..." % s3_path)

                        # try:
                        # client.delete_object(Bucket=bucket, Key=s3_path)
                        # except:
                        # print "Unable to delete %s..." % s3_path
                    except botocore.exceptions.ClientError as e:
                        if e.response['Error']['Code'] == "404":
                            # The object does not exist.
                            self.logger.debug(f"s3 ops raised a botocore ClientError!")
                            self.logger.debug("Uploading %s..." % s3_path)
                            self.s3.upload_file(Key=s3_path, Bucket=self.bucketname, Filename=local_file)
                    except ValueError as e:
                        self.logger.debug(f"s3 ops raised a ValueError! <{e}>")
                        self.logger.debug("Uploading %s..." % s3_path)
                        self.s3.upload_file(Key=s3_path, Bucket=self.bucketname, Filename=local_file)

        else:
            self.logger.info("Uploading %s..." % destination_path)
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
            self.logger.info('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        self.response = getattr(self, args.command)()

    def pull(self):
        parser = ArgumentParser(description='Retrieve a file from s3')
        # prefixing the argument with -- means it's optional
        parser.add_argument("s3_path", help="s3 path of directory")
        parser.add_argument("local_path", help="local path to which directory should be moved")
        parser.add_argument("-r", "--recursive", dest='recursive', action='store_true',
                            help="use this flag to move an entire directory, retaining dir structure")
        parser.add_argument("-v", "--verbose", dest='verbose',
                            action="count", default=0)
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (s3_operations) and the subcommand (pull)
        args = parser.parse_args(sys.argv[2:])

        return self.get_from_s3(s3path=args.s3_path,
                                local_path=args.local_path,
                                move_directory=args.recursive)

    def push(self):
        parser = ArgumentParser(description='Move a file to s3')
        # prefixing the argument with -- means it's optional
        parser.add_argument("local_path", help="local path of file/dir to move")
        parser.add_argument("s3_path", help="destination path for files to move")
        parser.add_argument("-r", "--recursive", dest='recursive', action='store_true',
                            help="use this flag to move an entire directory, retaining dir structure")
        parser.add_argument("-v", "--verbose", dest='verbose',
                            action="count", default=0)
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (s3_operations) and the subcommand (push)
        args = parser.parse_args(sys.argv[2:])

        return self.move_to_s3(local_path=args.local_path,
                               destination_path=args.s3_path,
                               move_directory=args.recursive,
                               verbose=args.verbose)


if __name__ == '__main__':
    s3ops = S3ops()
    s3ops.cli(sys.argv[:])


def get_workspace_from_s3(log_level, s3_workspace_dir):
    """ Workspace is copied in full from S3 """
    try:
        s3ops = S3ops(bucketname='modeling-data.chesapeakebay.net', log_level=log_level)
    except EnvironmentError as e:
        print(e)
        print('run_step2_generatemodel; trying again')
        try:
            s3ops = S3ops(bucketname='modeling-data.chesapeakebay.net', log_level=log_level)
        except EnvironmentError as e:
            print(e)
            raise e
    # Workspace is copied.
    s3ops.get_from_s3(s3path=s3_workspace_dir,
                      local_path=get_workspace_dir(),
                      move_directory=True)
    print(f"copied s3 workspace from {s3_workspace_dir} to local location: {get_workspace_dir()}")