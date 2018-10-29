from datetime import datetime

import logging
import logging.config

from bayota_settings.base import *

logdir = parse_config()['output_directories']['logs']
os.makedirs(logdir, exist_ok=True)
logfilename = os.path.join(logdir, 'efficiencysubproblem_debug.log')


def set_up_logger():
    if not os.path.isfile(user_log_config):
        os.makedirs(user_config_dir, exist_ok=True)
        shutil.copyfile("default_logging_config.cfg", user_log_config)

    logging.config.fileConfig(user_log_config, defaults={'logfilename': logfilename},
                              disable_existing_loggers=False)


class MyLogFormatter(logging.Formatter):
    def format(self, record):
        location = '%s.%s:%s' % (record.name, record.funcName, record.lineno)
        msg = '%s %-100s %-8s %s' % (self.formatTime(record), location, record.levelname, record.msg)
        record.msg = msg
        return super(MyLogFormatter, self).format(record)


def get_output_dir():
    outputdir_top_level = parse_config()['output_directories']['general']
    print('outputdir_top_level is %s' % user_config)

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
    graphics_dir = parse_config()['output_directories']['graphics']

    # dirname = os.path.join(graphics_dir, 'temp_bayota_out_' + today.strftime('%Y%m%d') + h)
    os.makedirs(graphics_dir, exist_ok=True)
    return graphics_dir