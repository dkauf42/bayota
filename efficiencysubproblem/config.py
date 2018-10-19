import os
from definitions import ROOT_DIR
# from amplpy import AMPL, Environment

PROJECT_DIR = os.path.join(ROOT_DIR, 'efficiencysubproblem/')
AMPLAPP_DIR = os.path.join(ROOT_DIR, 'ampl/amplide.macosx64/')
LOGGING_CONFIG = os.path.join(PROJECT_DIR, 'logging_config.ini')

verbose = True