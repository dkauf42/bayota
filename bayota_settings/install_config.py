from datetime import datetime

import logging.config

# get directories from base config methods
from bayota_settings.base import *

logdir = parse_user_config()['output_directories']['logs']
os.makedirs(logdir, exist_ok=True)
logfilename = os.path.join(logdir, 'efficiencysubproblem_debug.log')

# # Check if running on AWS
# inaws = False
# s3 = None
# _S3BUCKET = ''
# try:
#     resp = requests.get('http://169.254.169.254', timeout=0.001)
#     print('In AWS')
#     inaws = True
#
#     import s3fs
#     s3 = s3fs.core.S3FileSystem(anon=False)
#     _S3BUCKET = 's3://modeling-data.chesapeakebay.net/'
# except:
#     print('Not In AWS')
#


def set_up_logger():
    make_log_config()

    logging.config.fileConfig(log_config, defaults={'logfilename': logfilename},
                              disable_existing_loggers=False)


def get_output_dir():
    outputdir_top_level = parse_user_config()['output_directories']['general']
    print('outputdir_top_level is %s' % outputdir_top_level)

    # # Output Path
    # today = datetime.now()
    # if today.hour < 12:
    #     h = "00"
    # else:
    #     h = "12"
    # dirname = os.path.join(outputdir_top_level, 'temp_bayota_out_' + today.strftime('%Y%m%d') + h)
    os.makedirs(outputdir_top_level, exist_ok=True)
    return outputdir_top_level


def get_graphics_dir():
    graphics_dir = parse_user_config()['output_directories']['graphics']

    # dirname = os.path.join(graphics_dir, 'temp_bayota_out_' + today.strftime('%Y%m%d') + h)
    os.makedirs(graphics_dir, exist_ok=True)
    return graphics_dir


def get_source_csvs_dir():
    datadir_top_level = parse_user_config()['data_directories']['sourcecsvs']
    if not os.path.isdir(datadir_top_level):
        raise ValueError('Source CSVs directory (%s) specified in config does not exist!' % datadir_top_level)

    return datadir_top_level


def get_raw_data_dir():
    rawdatadir = parse_user_config()['data_directories']['rawdata']
    if not os.path.isdir(rawdatadir):
        raise ValueError('Raw data directory (%s) specified in config does not exist!' % rawdatadir)

    return rawdatadir


def get_source_pickles_dir():
    source_pickles_top_level = parse_user_config()['temp_directories']['source_pickles']
    os.makedirs(source_pickles_top_level, exist_ok=True)

    return source_pickles_top_level


def get_abstract_models_dir():
    abstract_models_top_level = parse_user_config()['temp_directories']['abstract_models']
    os.makedirs(abstract_models_top_level, exist_ok=True)

    return abstract_models_top_level


def get_instance_data_dir():
    instance_data_top_level = parse_user_config()['temp_directories']['instance_data']
    os.makedirs(instance_data_top_level, exist_ok=True)

    return instance_data_top_level


def get_concrete_models_dir():
    concrete_models_top_level = parse_user_config()['temp_directories']['concrete_models']
    os.makedirs(concrete_models_top_level, exist_ok=True)

    return concrete_models_top_level