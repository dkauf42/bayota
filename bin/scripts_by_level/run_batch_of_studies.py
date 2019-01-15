#!/usr/bin/env python

"""
Example usage command:
    ./bin/scripts_by_level/run_batch_of_studies.py --dryrun -f /Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/bayota/bin/study_specs/batch_study_specs/maryland_counties.yaml
"""

import os
import sys
import logging
import itertools
import subprocess
from argparse import ArgumentParser

from efficiencysubproblem.src.spec_handler import read_spec, notdry
from bayota_settings.config_script import set_up_logger, get_bayota_version, \
    get_scripts_dir, get_run_specs_dir

logger = logging.getLogger('root')
if not logger.hasHandlers():
    set_up_logger()
    logger = logging.getLogger(__name__)

geo_expansion_file = os.path.join(get_run_specs_dir(), 'geography_expansions.yaml')


def main(batch_spec_file, dryrun=False, no_slurm=False):
    batchdict = read_spec(batch_spec_file)

    version = get_bayota_version()

    # Process geographies, and expand any if necessary
    GEOS = batchdict['geographies']
    expansiondict = read_spec(geo_expansion_file)
    expandedGEOS = []
    for g in GEOS:
        if isinstance(g, dict):  # check if GEOS are expansions
            expansion_name = g['expand']
            expandedGEOS = expandedGEOS + expansiondict[expansion_name]
        else:
            expandedGEOS.append(g)
    GEOS = expandedGEOS

    STUDIES = batchdict['study_specs']
    study_pairs = list(itertools.product(GEOS, STUDIES))

    logger.info('----------------------------------------------')
    logger.info('*********** BayOTA version %s *************' % version)
    logger.info('************** Batch of studies **************')
    logger.info('----------------------------------------------')

    tempstr = 'study' if len(study_pairs) == 1 else 'studies'
    logger.info('%d %s to be conducted: %s' %
                (len(study_pairs), tempstr, study_pairs))

    NUMNODES = 1
    PRIORITY = 5000
    SLURM_OUTPUT = 'slurm_out'
    single_study_script = os.path.join(get_scripts_dir(), 'run_single_study.py')

    for sp in study_pairs:
        geoname = sp[0]
        studyspecname = sp[1]
        spname = geoname+'_'+studyspecname

        CMD = f"{single_study_script} -g {geoname} -n {studyspecname}"
        if not no_slurm:
            # Create a job to submit to the HPC with sbatch
            sbatch_opts = f"--job-name={spname} " \
                          f"--nice={PRIORITY} " \
                          f"--nodes={NUMNODES} " \
                          f"--output={SLURM_OUTPUT} " \
                          f"--time=01:00:00 " # time requested in hour:minute:second
            CMD = "sbatch " + sbatch_opts + CMD

        # Submit the job
        logger.info(f'Job command is: "{CMD}"')
        if notdry(dryrun, logger, '--Dryrun- Would submit command'):
            subprocess.Popen([CMD], shell=True)

    return 0  # a clean, no-issue, exit


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()
    one_or_the_other = parser.add_mutually_exclusive_group(required=True)
    one_or_the_other.add_argument("-n", "--batch_spec_name", dest="batch_name", default=None,
                                  help="name for this batch, which should match the batch specification file")
    one_or_the_other.add_argument("-f", "--batch_spec_filepath", dest="batch_spec_filepath", default=None,
                                  help="path for this batch's specification file")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("--no_slurm", action='store_true',
                        help="don't use AWS or slurm facilities")

    opts = parser.parse_args()

    if not opts.batch_spec_filepath:  # name was specified
        opts.batch_spec_file = os.path.join('study_model_specs', opts.batch_name + '.yaml')
    else:  # filepath was specified
        opts.batch_spec_file = opts.batch_spec_filepath

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    sys.exit(main(opts.batch_spec_file,
                  dryrun=opts.dryrun, no_slurm=opts.no_slurm))
