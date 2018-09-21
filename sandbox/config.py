import os
from definitions import ROOT_DIR

PROJECT_DIR = os.path.join(ROOT_DIR, 'sandbox/')

verbose = False


def get_outputdir():
    return os.path.join(PROJECT_DIR, 'output/')