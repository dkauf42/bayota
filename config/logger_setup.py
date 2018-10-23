import os

import logging
import logging.config

from .settings import get_logger_path

logconfig_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging_config.cfg')
# print(logconfig_file)

logfilename = os.path.join(get_logger_path(), 'efficiencysubproblem_debug.log')
# print(logfilename)


def set_up_logger():
    logging.config.fileConfig(logconfig_file, defaults={'logfilename': logfilename},
                              disable_existing_loggers=False)


class MyLogFormatter(logging.Formatter):
    def format(self, record):
        location = '%s.%s:%s' % (record.name, record.funcName, record.lineno)
        msg = '%s %-100s %-8s %s' % (self.formatTime(record), location, record.levelname, record.msg)
        record.msg = msg
        return super(MyLogFormatter, self).format(record)