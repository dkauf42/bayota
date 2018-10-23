import os

# import logging
# import logging.config

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# logconfig_file = (os.path.dirname(PROJECT_DIR), 'logging_config.cfg')
# logfilename = os.path.join(PROJECT_DIR, 'log', 'efficiencysubproblem_debug.log')
#
#
# def set_up_logger():
#     logging.config.fileConfig(logconfig_file, defaults={'logfilename': logfilename},
#                               disable_existing_loggers=False)
#
#
# class MyLogFormatter(logging.Formatter):
#     def format(self, record):
#         location = '%s.%s:%s' % (record.name, record.funcName, record.lineno)
#         msg = '%s %-100s %-8s %s' % (self.formatTime(record), location, record.levelname, record.msg)
#         record.msg = msg
#         return super(MyLogFormatter, self).format(record)