from datetime import datetime

import logging.config

# get directories from base config methods
from bayota_settings.base import *

logdir = parse_user_config()['output_directories']['logs']
os.makedirs(logdir, exist_ok=True)
logfilename = os.path.join(logdir, 'efficiencysubproblem_debug.log')


def set_up_logger():
    make_log_config()

    logging.config.fileConfig(log_config, defaults={'logfilename': logfilename},
                              disable_existing_loggers=False)


def get_data_dir():
    datadir_top_level = parse_user_config()['data_directories']['sourcecsvs']
    if not os.path.isdir(datadir_top_level):
        raise ValueError('Data directory specified in config <%s> does not exist!')

    return datadir_top_level


def get_temp_dir():
    tempdir_top_level = parse_user_config()['output_directories']['temp']
    os.makedirs(tempdir_top_level, exist_ok=True)

    return tempdir_top_level


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