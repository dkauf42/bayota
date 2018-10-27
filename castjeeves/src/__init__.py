"""
Module for cast_opt_tests
"""

import os
from settings.output_paths import get_output_dir
outdir = get_output_dir()
# import requests

# from .jeeves import Jeeves

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
_WORKINGDIR = os.path.abspath(os.path.join(os.getcwd(), '..'))

# # Check if running on AWS
# inaws = False
# s3 = None
# _S3BUCKET = ''
# try:
#     resp = requests.get('http://169.254.169.254', timeout=0.001)
#     print('In AWS')
#     inaws = True
#
#     import s3fs
#     s3 = s3fs.core.S3FileSystem(anon=False)
#     _S3BUCKET = 's3://modeling-data.chesapeakebay.net/'
# except:
#     print('Not In AWS')
#

def get_datadir(path=''):
    if not path:
        retval = os.path.join(_ROOT, 'data/')
    else:
        retval = os.path.join(_ROOT, 'data/', path)
    return retval


def get_tempdir():
    dirname = os.path.join(_ROOT, 'temp/')
    os.makedirs(dirname, exist_ok=True)
    return dirname


def get_outputdir():
    # return os.path.join(_WORKINGDIR, 'output/')
    return outdir


def get_sqlsourcetabledir():
    return os.path.join(_ROOT, 'data/test_source/')


def get_sqlmetadatatabledir():
    return os.path.join(_ROOT, 'data/test_metadata/')
