"""

"""
import os
import sys

from bayota_settings.base import get_bayota_version, get_workspace_dir, \
    get_source_csvs_dir, get_raw_data_dir, get_metadata_csvs_dir
from bayota_settings.log_setup import root_logger_setup
from bayota_util.s3_operations import S3ops


def main(log_level='INFO') -> int:
    logger = root_logger_setup(consolehandlerlevel=log_level, filehandlerlevel='DEBUG')
    logger.debug(locals())

    version = get_bayota_version()
    logger.info('v----------------------------------------------v')
    logger.info(' ******* %s *******' % ('BayOTA version ' + version).center(30, ' '))
    logger.info(' ********** Moving source data to s3 **********')
    logger.info('^----------------------------------------------^')

    """ Data directories are copied to S3 """
    ws_dir_name = os.path.basename(os.path.normpath(get_workspace_dir()))
    s3_ws_base_path = 'optimization/ws_copies/'
    s3_ws_dir = s3_ws_base_path + ws_dir_name

    # Relative path (for source CSV files)
    common_path = os.path.commonpath([get_workspace_dir(), get_source_csvs_dir()])
    relative_path_for_sourcecsv_dir = os.path.relpath(get_source_csvs_dir(), common_path)
    s3_sourcecsvs_dir = s3_ws_dir + '/' + relative_path_for_sourcecsv_dir + '/'
    # Relative path (for metadata CSV files)
    common_path = os.path.commonpath([get_workspace_dir(), get_metadata_csvs_dir()])
    relative_path_for_metadatacsv_dir = os.path.relpath(get_metadata_csvs_dir(), common_path)
    s3_metadatacsvs_dir = s3_ws_dir + '/' + relative_path_for_metadatacsv_dir + '/'
    # Relative path (for raw data files)
    common_path = os.path.commonpath([get_workspace_dir(), get_raw_data_dir()])
    relative_path_for_rawdata_dir = os.path.relpath(get_raw_data_dir(), common_path)
    s3_rawdata_dir = s3_ws_dir + '/' + relative_path_for_rawdata_dir + '/'

    s3ops = None
    try:
        s3ops = S3ops(bucketname='modeling-data.chesapeakebay.net', log_level=log_level)
    except EnvironmentError as e:
        logger.info(e)
        logger.info('trying again')
        try:
            s3ops = S3ops(bucketname='modeling-data.chesapeakebay.net', log_level=log_level)
        except EnvironmentError as e:
            logger.error(e)
            raise e
    # Source CSV files are copied.
    logger.info(f"copying source csv files from {get_source_csvs_dir()} to the s3 location: {s3_sourcecsvs_dir}")
    s3ops.move_to_s3(local_path=get_source_csvs_dir(),
                     destination_path=f"{s3_sourcecsvs_dir}",
                     move_directory=True)
    # Metadata CSV files are copied.
    logger.info(f"copying metadata csv files from {get_metadata_csvs_dir()} to the s3 location: {s3_metadatacsvs_dir}")
    s3ops.move_to_s3(local_path=get_metadata_csvs_dir(),
                     destination_path=f"{s3_metadatacsvs_dir}",
                     move_directory=True)
    # Raw Data files are copied.
    logger.info(f"copying specifcation files from {get_raw_data_dir()} to the s3 location: {s3_rawdata_dir}")
    s3ops.move_to_s3(local_path=get_raw_data_dir(),
                     destination_path=f"{s3_rawdata_dir}",
                     move_directory=True)

    return 0  # a clean, no-issue, exit


if __name__ == '__main__':
    sys.exit(main())
