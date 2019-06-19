#!/usr/bin/env python

"""
Example usage command:
    ./bin/scripts_by_level/run_single_study.py --dryrun -f /Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/bayota/bin/study_specs/single_study_specs/adamsPA_0001.yaml
"""

import os
import time
import logging
import cloudpickle
from argparse import ArgumentParser

from bayom_e.src.spec_handler import notdry
from bayom_e.src.model_handling.utils import load_model_pickle
from bin.run_scripts import run_step2_generatemodel

from bayota_settings.base import get_output_dir, get_scripts_dir, get_model_instances_dir, \
    get_bayota_version, get_single_study_specs_dir, get_experiment_specs_dir
from bayota_settings.log_setup import root_logger_setup

logger = root_logger_setup()

outdir = get_output_dir()


def main(dryrun=False):
    logprefix = '** Blackbox Experiment **: '
    saved_model_file = os.path.join(get_model_instances_dir(),
                                           'modelinstance_costmin_total_percentreduction_CalvertMD.pickle')

    run_step2_generatemodel.main(model_spec_file='costmin_total_percentreduction',
                                 geography_name='CalvertMD',
                                 saved_model_file=saved_model_file,
                                 dryrun=False, baseloadingfilename='2010NoActionLoads.csv')

    mdlhandler = load_model_pickle(savepath=saved_model_file, dryrun=dryrun, logprefix=logprefix)

    mdlhandler.model

