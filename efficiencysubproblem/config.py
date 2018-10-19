import os
from definitions import ROOT_DIR
# from amplpy import AMPL, Environment

from io import StringIO
import logging
import logging.config

PROJECT_DIR = os.path.join(ROOT_DIR, 'efficiencysubproblem/')
AMPLAPP_DIR = os.path.join(ROOT_DIR, 'ampl/amplide.macosx64/')

verbose = True


# SET UP THE LOGGER
class MyLogFormatter(logging.Formatter):
    def format(self, record):
        location = '%s.%s:%s' % (record.name, record.funcName, record.lineno)
        msg = '%s %-100s %-8s %s' % (self.formatTime(record), location, record.levelname, record.msg)
        record.msg = msg
        return super(MyLogFormatter, self).format(record)


logger_config_str = u'''
[loggers]
keys=root

[handlers]
keys: consoleHandler,fileHandler

[formatters]
keys: detailedFormatter,simpleFormatter,reallysimpleFormatter

[logger_root]
level=DEBUG
handlers=consoleHandler,fileHandler

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=reallysimpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=handlers.TimedRotatingFileHandler
interval=midnight
backupCount=5
level=DEBUG
formatter=detailedFormatter
args=('efficiencysubproblem/output/testSuite.log',)

[formatter_reallysimpleFormatter]
format: %(levelname)-8s %(message)s

[formatter_simpleFormatter]
format: %(asctime)s:%(levelname)-8s- %(module)s - %(message)s
datefmt=%H:%M:%S

[formatter_detailedFormatter]
class=efficiencysubproblem.config.MyLogFormatter
'''

LOGGERCFG = StringIO(logger_config_str)
# format=%(asctime)s:%(levelname)-8s- %(module)-35s [%(funcName)s:%(lineno)s] - %(message)s
# datefmt=%Y-%m-%d %H:%M:%S