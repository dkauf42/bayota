#!/usr/bin/env python
"""
Run this when switching versions so that the data files are in the necessary S3 location
"""
import sys

from bayota_settings.base import get_bayota_version, get_source_csvs_dir, get_raw_data_dir, get_metadata_csvs_dir
from bayota_settings.log_setup import root_logger_setup
from bayota_util.s3_operations import establish_s3_connection


def main(log_level='INFO') -> int:
    """ Data directories are copied to S3 """

    logger = root_logger_setup(consolehandlerlevel=log_level, filehandlerlevel='DEBUG')
    logger.debug(locals())

    version = get_bayota_version()
    logger.info('v----------------------------------------------v')
    logger.info(' ******* %s *******' % ('BayOTA version ' + version).center(30, ' '))
    logger.info(' ********** Moving source data to s3 **********')
    logger.info('^----------------------------------------------^')

    # Connection with S3 is established.
    s3ops = establish_s3_connection(log_level, logger)

    # Source CSV files are copied.
    local_path = get_source_csvs_dir(s3=False)
    s3_path = get_source_csvs_dir(s3=True)
    logger.info(f"copying source csv files from {local_path} to the s3 location: {s3_path}")
    s3ops.move_to_s3(local_path=local_path, destination_path=s3_path, move_directory=True)

    # Metadata CSV files are copied.
    local_path = get_metadata_csvs_dir(s3=False)
    s3_path = get_metadata_csvs_dir(s3=True)
    logger.info(f"copying metadata csv files from {local_path} to the s3 location: {s3_path}")
    s3ops.move_to_s3(local_path=local_path, destination_path=s3_path, move_directory=True)

    # Raw Data files are copied.
    local_path = get_raw_data_dir(s3=False)
    s3_path = get_raw_data_dir(s3=True)
    logger.info(f"copying other raw data files from {local_path} to the s3 location: {s3_path}")
    s3ops.move_to_s3(local_path=local_path, destination_path=s3_path, move_directory=True)

    return 0  # a clean, no-issue, exit


if __name__ == '__main__':
    sys.exit(main())
