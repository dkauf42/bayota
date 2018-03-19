"""
Module for cast_opt_tests
"""

import os

_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_data(path=''):
    if not path:
        retval = os.path.join(_ROOT, 'data')
    else:
        retval = os.path.join(_ROOT, 'data/', path)
    return retval

def get_tempdir():
    return os.path.join(_ROOT, 'temp')
