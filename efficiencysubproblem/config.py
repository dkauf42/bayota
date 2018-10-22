import os
from definitions import ROOT_DIR
# from amplpy import AMPL, Environment

import logging
import logging.config

verbose = True

PROJECT_DIR = os.path.join(ROOT_DIR, 'efficiencysubproblem/')
AMPLAPP_DIR = os.path.join(ROOT_DIR, 'ampl/amplide.macosx64/')

logconfig_file = (os.path.join(PROJECT_DIR, 'logging_config.cfg'))
logfilename = os.path.join(PROJECT_DIR, 'output', 'testSuite.log')


def set_up_logger():
    logging.config.fileConfig(logconfig_file, defaults={'logfilename': logfilename},
                              disable_existing_loggers=False)


class MyLogFormatter(logging.Formatter):
    def format(self, record):
        location = '%s.%s:%s' % (record.name, record.funcName, record.lineno)
        msg = '%s %-100s %-8s %s' % (self.formatTime(record), location, record.levelname, record.msg)
        record.msg = msg
        return super(MyLogFormatter, self).format(record)