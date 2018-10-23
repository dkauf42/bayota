import os
import logging
import logging.config

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'output/')

logconfig_file = (os.path.join(PROJECT_DIR, 'logging_config.cfg'))
logfilename = os.path.join(PROJECT_DIR, 'log', 'sandbox_debug.log')


# Check if running on AWS
import requests
inaws = False
s3 = None
_S3BUCKET = ''
try:
    resp = requests.get('http://169.254.169.254', timeout=0.001)
    print('AWS url response: %s' % resp)
    if 'ami' in resp:
        print('In AWS')
        inaws = True
    else:
        raise ConnectionError

    import s3fs
    s3 = s3fs.core.S3FileSystem(anon=False)
    _S3BUCKET = 's3://modeling-data.chesapeakebay.net/'
except:
    print('Not In AWS')

# ** Set up logging **


def set_up_logger():
    logging.config.fileConfig(logconfig_file, defaults={'logfilename': logfilename},
                              disable_existing_loggers=False)


class MyLogFormatter(logging.Formatter):
    def format(self, record):
        location = '%s.%s:%s' % (record.name, record.funcName, record.lineno)
        msg = '%s %-100s %-8s %s' % (self.formatTime(record), location, record.levelname, record.msg)
        record.msg = msg
        return super(MyLogFormatter, self).format(record)
