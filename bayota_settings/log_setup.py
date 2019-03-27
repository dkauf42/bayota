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

root_logfilename = 'efficiencysubproblem_debug.log'
root_logfilename = os.path.join(get_logging_dir(), root_logfilename)


def level_from_str(levelstr):
    return logging.getLevelName(levelstr)


class MyCustomFormatter(logging.Formatter):

    FORMATS = {
        logging.ERROR: logging.Formatter("ERROR: %(msg)s"),
        logging.WARNING: logging.Formatter("WARNING: %(msg)s"),
        logging.DEBUG: logging.Formatter("DEBUG: %(module)s:%(lineno)s %(msg)s"),
        "DEFAULT": reallysimpleFormatter,
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        return formatter.format(record)


def root_logger_setup(consolehandlerlevel='INFO', filehandlerlevel='DEBUG'):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # set the logger itself to the lowest potential level

    if not root_logger.hasHandlers():
        """ set handlers to other, higher logging levels"""
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(MyCustomFormatter())
        console_handler.setLevel(getattr(logging, consolehandlerlevel.upper()))
        root_logger.addHandler(console_handler)

        # File Handler
        file_handler = logging.handlers.TimedRotatingFileHandler(filename=root_logfilename, when='midnight',
                                                                 interval=1, backupCount=7)
        file_handler.setFormatter(detailedFormatter)
        file_handler.setLevel(getattr(logging, filehandlerlevel.upper()))
        root_logger.addHandler(file_handler)

    return root_logger


def set_up_detailedfilelogger(loggername: str, level: str,
                              filename=None,
                              also_logtoconsole: bool = False):
    logging_level = getattr(logging, level.upper())

    logger = logging.getLogger(loggername)
    logger.setLevel(logging_level)

    # File Handler
    if not filename:
        file_handler = logging.handlers.TimedRotatingFileHandler(filename=root_logfilename, when='midnight',
                                                                 interval=1, backupCount=7)
    else:
        logfilename = os.path.join(get_logging_dir(), filename)
        file_handler = logging.handlers.TimedRotatingFileHandler(filename=logfilename, when='midnight',
                                                                 interval=1, backupCount=7)

    file_handler.setFormatter(detailedFormatter)
    file_handler.setLevel(logging_level)
    logger.addHandler(file_handler)

    if also_logtoconsole:
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(reallysimpleFormatter)
        console_handler.setLevel(logging_level)
        logger.addHandler(console_handler)

    return logger


# class MyDetailedLogFormatter(logging.Formatter):
#     """Note: this class is used in the log configuration file (typically stored in ~/.config/$USER/)
#     """
#     def format(self, record):
#         location = '%s.%s:%s' % (record.name, record.funcName, record.lineno)
#         msg = '%s %-60s %-8s %s' % (self.formatTime(record), location, record.levelname, record.msg)
#         record.msg = msg
#         return super(MyDetailedLogFormatter, self).format(record)
