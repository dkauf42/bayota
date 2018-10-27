import os
import shutil

import logging
import logging.config

from settings.output_paths import get_logging_dir
logdir = get_logging_dir()

user_log_config_dir = os.path.expanduser("~") + "/.config/danny"
user_log_config = user_log_config_dir + "/bayota_logging_config.cfg"

logfilename = os.path.join(logdir, 'efficiencysubproblem_debug.log')


def set_up_logger():
    if not os.path.isfile(user_log_config):
        os.makedirs(user_log_config_dir, exist_ok=True)
        shutil.copyfile("default_logging_config.cfg", user_log_config)

    logging.config.fileConfig(user_log_config, defaults={'logfilename': logfilename},
                              disable_existing_loggers=False)


class MyLogFormatter(logging.Formatter):
    def format(self, record):
        location = '%s.%s:%s' % (record.name, record.funcName, record.lineno)
        msg = '%s %-100s %-8s %s' % (self.formatTime(record), location, record.levelname, record.msg)
        record.msg = msg
        return super(MyLogFormatter, self).format(record)