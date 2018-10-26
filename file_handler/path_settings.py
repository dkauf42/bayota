from datetime import datetime
import os

outputdir_toplevel = "/Users/Danny/"


def get_outdir_path():
    today = datetime.now()
    if today.hour < 12:
        h = "00"
    else:
        h = "12"
    dirname = os.path.join(outputdir_toplevel, 'temp_bayota_out_' + today.strftime('%Y%m%d') + h)
    os.makedirs(dirname, exist_ok=True)
    return dirname


def get_graphics_path():
    dirname = os.path.join(get_outdir_path(), 'graphics')
    os.makedirs(dirname, exist_ok=True)
    return dirname


def get_logger_path():
    dirname = os.path.join(get_outdir_path(), 'log')
    os.makedirs(dirname, exist_ok=True)
    return dirname
