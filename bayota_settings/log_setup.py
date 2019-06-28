import os
import sys
import logging
import logging.handlers

from bayota_settings.base import get_logging_dir, log_config

from bayota_util.spec_handler import read_spec

log_format_config = read_spec(log_config)

consoleINFOfmt = logging.Formatter(log_format_config['formatters']['console']['info'][0],
                                   log_format_config['formatters']['console']['info'][1])
consoleDEBUGfmt = logging.Formatter(log_format_config['formatters']['console']['debug'][0],
                                    log_format_config['formatters']['console']['debug'][1])

fileINFOfmt = logging.Formatter(log_format_config['formatters']['file']['info'][0],
                                log_format_config['formatters']['file']['info'][1])
fileDEBUGfmt = logging.Formatter(log_format_config['formatters']['file']['debug'][0],
                                 log_format_config['formatters']['file']['debug'][1])

defaultfmt = logging.Formatter(log_format_config['formatters']['default'][0],
                               log_format_config['formatters']['default'][1])

root_logfilename = 'efficiencysubproblem_debug.log'
root_logfilename = os.path.join(get_logging_dir(), root_logfilename)


def level_from_str(levelstr):
    return logging.getLevelName(levelstr)


class MyCustomConsoleFormatter(logging.Formatter):

    FORMATS = {
        logging.INFO: consoleINFOfmt,
        logging.DEBUG: consoleDEBUGfmt,
        "DEFAULT": defaultfmt,
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        return formatter.format(record)


class MyCustomFileFormatter(logging.Formatter):

    FORMATS = {
        logging.INFO: fileINFOfmt,
        logging.DEBUG: fileDEBUGfmt,
        "DEFAULT": defaultfmt,
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
        console_handler.setFormatter(MyCustomConsoleFormatter())
        console_handler.setLevel(getattr(logging, consolehandlerlevel.upper()))
        root_logger.addHandler(console_handler)

        # File Handler
        file_handler = logging.handlers.TimedRotatingFileHandler(filename=root_logfilename, when='midnight',
                                                                 interval=1, backupCount=7)
        file_handler.setFormatter(MyCustomFileFormatter())
        file_handler.setLevel(getattr(logging, filehandlerlevel.upper()))
        root_logger.addHandler(file_handler)

    return root_logger


def set_up_detailedfilelogger(loggername: str, level: str,
                              filename=None,
                              also_logtoconsole: bool = False,
                              add_filehandler_if_already_exists: bool = True,
                              add_consolehandler_if_already_exists: bool = True):
    logging_level = getattr(logging, level.upper())

    logger = logging.getLogger(loggername)
    logger.setLevel(logging_level)

    def addfilehandler():
        # File Handler
        if not filename:
            file_handler = logging.handlers.TimedRotatingFileHandler(filename=root_logfilename, when='midnight',
                                                                     interval=1, backupCount=7)
        else:
            logfilename = os.path.join(get_logging_dir(), filename)
            file_handler = logging.handlers.TimedRotatingFileHandler(filename=logfilename, when='midnight',
                                                                     interval=1, backupCount=7)

        file_handler.setFormatter(MyCustomFileFormatter())
        file_handler.setLevel(logging_level)
        logger.addHandler(file_handler)

    def addconsolehandler():
        if also_logtoconsole:
            # Console Handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(MyCustomConsoleFormatter())
            console_handler.setLevel(logging_level)
            logger.addHandler(console_handler)

    if logger.hasHandlers():
        if add_filehandler_if_already_exists:
            addfilehandler()
        if add_consolehandler_if_already_exists:
            addconsolehandler()
    else:
        addfilehandler()
        addconsolehandler()

    return logger


# class MyDetailedLogFormatter(logging.Formatter):
#     """Note: this class is used in the log configuration file (typically stored in ~/.config/$USER/)
#     """
#     def format(self, record):
#         location = '%s.%s:%s' % (record.name, record.funcName, record.lineno)
#         msg = '%s %-60s %-8s %s' % (self.formatTime(record), location, record.levelname, record.msg)
#         record.msg = msg
#         return super(MyDetailedLogFormatter, self).format(record)
