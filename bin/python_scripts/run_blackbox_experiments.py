#!/usr/bin/env python

"""
Example usage command:
    ./bin/scripts_by_level/run_single_study.py --dryrun -f /Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/bayota/bin/study_specs/single_study_specs/adamsPA_0001.yaml
"""

import math
import yaml
import logging
import numpy as np
import pandas as pd
from itertools import product
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-l", "--log_level", dest="loglvl", default='info', type=str.lower,
                    choices=['debug', 'info', 'warning', 'error', 'critical'],
                    help="change logging level to {debug, info, warning, error, critical}")
opts = parser.parse_args()

# Set up logging
level_config = {'debug': logging.DEBUG, 'info': logging.INFO,
                'warning': logging.WARNING, 'error': logging.ERROR, 'critical': logging.CRITICAL}
log_level = level_config[opts.loglvl.lower()]
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)
logging.debug('This will get logged')

import pyomo.environ as pyo

from bayota_settings.base import get_bayota_version
logging.info("using bayota version '%s'" % get_bayota_version())

from bayota_settings.base import get_source_csvs_dir
logging.info("getting source csvs from: '%s'" % get_source_csvs_dir())

from bayota_util.spec_and_control_handler import read_spec
from bayom_e.data_handling.data_interface import get_dataplate
from bayom_e.model_handling.interface import check_for_problems_in_data_before_model_construction

from bayom_e.model_handling.builders.nonlinear import NonlinearVariant
from bayom_e.model_handling.builders.linear import LinearVariant

from bayom_e.model_handling.builders.modelbuilder import ModelBuilder

from bayom_e.model_handling.interface import build_model

from bayom_e.model_handling.utils import model_as_func_for_pygmo
import pygmo as pg

# modelspec = '/Users/Danny/bayota_ws_0.1b2/specification_files/model_specs/costmin_total_Npercentreduction_updated_percentreduction.yaml'
model_spec_name = 'costmin_total_Npercentreduction_updated_percentreduction'
geoscale = 'county'
geoentities = 'Adams, PA'
baseloadingfilename = '2010NoActionLoads_updated.csv'

# with open(modelspec, 'r') as stream:
#     modelspec_dict = yaml.safe_load(stream)
# modelspec_dict['variant'] = 'lp'
# display(modelspec_dict)

my_model, dp = build_model(model_spec_name, geoscale, geoentities, baseloadingfilename,
                               savedata2file=False, log_level='INFO')

prob_dim = len(my_model.x)
logging.info(f"--DIAGNOSTIC--\nprob_dim={prob_dim}")

my_prob = model_as_func_for_pygmo(prob_dim, pyomo_model=my_model,
                                      objective1_name='total_cost_expr', objective1_indexer=None, objective1_sign=1,
                                      objective2_name='percent_reduction_expr', objective2_indexer='N', objective2_sign=-1)

# create UDP
prob = pg.problem(my_prob)

# create population
pop = pg.population(prob, size=20)

# select algorithm
algo = pg.algorithm(pg.nsga2(gen=40))

# run optimization
pop = algo.evolve(pop)

# extract results
fits, vectors = pop.get_f(), pop.get_x()
logging.info(f"--DIAGNOSTIC--\nfits={fits}")

# extract and print non-dominated fronts
ndf, dl, dc, ndr = pg.fast_non_dominated_sorting(fits)

