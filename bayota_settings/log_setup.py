import os
import sys
import logging
import logging.handlers

from bayota_settings.base import get_logging_dir, log_config

from efficiencysubproblem.src.spec_handler import read_spec

# reallysimpleFormatter = logging.Formatter("%(levelname)-8s %(message)s")
#
# simpleFormatter = logging.Formatter("%(asctime)s:%(levelname)-8s- %(module)s - %(message)s",
#                                     "%H:%M:%S")

log_format_config = read_spec(log_config)

reallysimpleFormatter = logging.Formatter(log_format_config['formatters']['reallysimple'][0],
                                          log_format_config['formatters']['reallysimple'][1])
simpleFormatter = logging.Formatter(log_format_config['formatters']['simple'][0],
                                    log_format_config['formatters']['simple'][1])
detailedFormatter = logging.Formatter(log_format_config['formatters']['detailed'][0],
                                      log_format_config['formatters']['detailed'][1])


def root_logger_setup():
    root_logger = logging.getLogger('root')

    if not root_logger.hasHandlers():
        root_logfilename = 'efficiencysubproblem_debug.log'
        logfilename = os.path.join(get_logging_dir(), root_logfilename)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(reallysimpleFormatter)
        console_handler.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)

        # File Handler
        file_handler = logging.handlers.TimedRotatingFileHandler(filename=logfilename, when='midnight',
                                                                 interval=1, backupCount=7)
        file_handler.setFormatter(detailedFormatter)
        root_logger.addHandler(file_handler)

        root_logger.setLevel(logging.DEBUG)

    return root_logger


def set_up_detailedfilelogger(loggername: str, filename: str, level,
                              also_logtoconsole: bool = False):
    logfilename = os.path.join(get_logging_dir(), filename)

    logger = logging.getLogger(loggername)

    if not logger.hasHandlers():
        # File Handler
        file_handler = logging.handlers.TimedRotatingFileHandler(filename=logfilename, when='midnight',
                                                                 interval=1, backupCount=7)
        file_handler.setFormatter(detailedFormatter)
        logger.addHandler(file_handler)

        if also_logtoconsole:
            # Console Handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(reallysimpleFormatter)
            console_handler.setLevel(logging.INFO)
            logger.addHandler(console_handler)

    logger.setLevel(level)

    return logger


# class MyDetailedLogFormatter(logging.Formatter):
#     """Note: this class is used in the log configuration file (typically stored in ~/.config/$USER/)
#     """
#     def format(self, record):
#         location = '%s.%s:%s' % (record.name, record.funcName, record.lineno)
#         msg = '%s %-60s %-8s %s' % (self.formatTime(record), location, record.levelname, record.msg)
#         record.msg = msg
#         return super(MyDetailedLogFormatter, self).format(record)
