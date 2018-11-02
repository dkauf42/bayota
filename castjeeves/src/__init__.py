"""
Module for cast_opt_tests
"""

import os
from bayota_settings.install_config import get_output_dir, get_data_dir, get_temp_dir
outdir = get_output_dir()
datadir = get_data_dir()
tempdir = get_temp_dir()
# import requests

# from .jeeves import Jeeves

# _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# _WORKINGDIR = os.path.abspath(os.path.join(os.getcwd(), '..'))

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


def get_datadir():
    return datadir


def get_tempdir():
    return tempdir


def get_sqlsourcetabledir():
    return os.path.join(datadir, 'test_source/')


def get_sqlmetadatatabledir():
    return os.path.join(datadir, 'test_metadata/')
