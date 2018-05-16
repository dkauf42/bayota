"""
Module for cast_opt_tests
"""

import os

# Check if running on AWS
# import urllib
from urllib.request import urlopen
# html = urlopen("http://www.google.com/")

meta = 'http://169.254.169.254/latest/meta-data' #/ami-id'
# req = urllib.request(meta)
try:
    response = urlopen(meta).read()
    if 'ami' in response:
        _msg = 'I am in AWS running on {}'.format(response)
    else:
        _msg = 'I am in dev - no AWS AMI'
except Exception as nometa:
    _msg = 'no metadata, not in AWS'

print(_msg)
# import s3fs

# s3 = s3fs.core.S3FileSystem(anon=False)

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# _S3BUCKET = 's3://modeling-data.chesapeakebay.net/'


def get_datadir(path=''):
    if not path:
        retval = os.path.join(_ROOT, 'data/')
    else:
        retval = os.path.join(_ROOT, 'data/', path)
    return retval


def get_tempdir():
    return os.path.join(_ROOT, 'temp/')


def get_outputdir():
    return os.path.join(_ROOT, 'output/')


def get_sqlsourcetabledir():
    return os.path.join(_ROOT, 'data/test_source/')
