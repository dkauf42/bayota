import math
import yaml
import numpy as np
import pandas as pd
import pyomo.environ as pyo

from bayota_settings.base import get_bayota_version
print("using bayota version '%s'" % get_bayota_version())

from bayota_settings.base import get_source_csvs_dir
print("getting source csvs from: '%s'" % get_source_csvs_dir())

from bayom_e.model_handling.interface import build_model

modelspec = '/Users/Danny/bayota_ws_0.1b1.dev2/specification_files/model_specs/costmin_total_Npercentreduction_updated.yaml'
geoscale = 'county'
geoentities = 'Adams, PA'
baseloadingfilename = '2010NoActionLoads_updated.csv'

with open(modelspec, 'r') as stream:
    modelspec_dict = yaml.safe_load(stream)

modelspec_dict['variant'] = 'lp'

print(modelspec_dict)
my_model, dp = build_model(modelspec_dict, geoscale, geoentities, baseloadingfilename,
                           savedata2file=False, log_level='INFO')