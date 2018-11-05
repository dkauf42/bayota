"""
Module for castjeeves src
"""

import os
from bayota_settings.config_script import get_source_csvs_dir
sourcecsvsdir = get_source_csvs_dir()


def get_sqlsourcetabledir():
    return os.path.join(sourcecsvsdir, 'test_source/')


def get_sqlmetadatatabledir():
    return os.path.join(sourcecsvsdir, 'test_metadata/')
