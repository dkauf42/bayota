#!/usr/bin/env python

"""
Example usage command:
    ./bin/scripts_by_level/run_step0_batch_of_studies.py --dryrun -f /Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/bayota/bin/study_specs/batch_study_specs/maryland_counties.yaml
"""

import os
import sys
import uuid
import yaml
import logging
import itertools
import subprocess
from argparse import ArgumentParser

from efficiencysubproblem.src.spec_handler import read_spec, notdry
from bayota_settings.config_script import set_up_logger, get_bayota_version, \
    get_scripts_dir, get_run_specs_dir, get_control_dir
from castjeeves.src.jeeves import Jeeves

logger = logging.getLogger('root')
if not logger.hasHandlers():
    set_up_logger()
    logger = logging.getLogger(__name__)

geo_expansion_file = os.path.join(get_run_specs_dir(), 'geography_expansions.yaml')

jeeves = Jeeves()


def main(batch_spec_file, dryrun=False, no_slurm=False):
    version = get_bayota_version()
    logger.info('----------------------------------------------')
    logger.info('*********** BayOTA version %s *************' % version)
    logger.info('************** Batch of studies **************')
    logger.info('----------------------------------------------')

    geo_scale, study_pairs, control_options = read_batch_spec_file(batch_spec_file)

    tempstr = 'study' if len(study_pairs) == 1 else 'studies'
    logger.info('%d %s to be conducted: %s' %
                (len(study_pairs), tempstr, study_pairs))

    # Set SLURM parameters
    NUMNODES = 1
    PRIORITY = 5000
    SLURM_OUTPUT = 'slurm_out'
    single_study_script = os.path.join(get_scripts_dir(), 'run_step1_single_study.py')

    for sp in study_pairs:
        geoname = sp[0]
        filesafegeostring = geoname.replace(' ', '').replace(',', '')
        studyspecname = sp[1]
        spname = filesafegeostring+'_'+studyspecname

        # Generate a control file with a unique identifier (uuid4)
        dct = {"geography_scale": geo_scale, "geography_entity": geoname,
               "study_spec": studyspecname, "control_options": control_options}
        unique_control_file = os.path.join(get_control_dir(), 'step1_study_control_' + str(uuid.uuid4()) + '.yaml')
        with open(unique_control_file, "w") as f:
            yaml.safe_dump(dct, f, default_flow_style=False)

        # Create a job to submit to the queue
        CMD = f"{single_study_script} -cf {unique_control_file}"
        if not no_slurm:
            sbatch_opts = f"--job-name={spname} " \
                          f"--nice={PRIORITY} " \
                          f"--nodes={NUMNODES} " \
                          f"--output={SLURM_OUTPUT} " \
                          f"--time=01:00:00 "  # time requested in hour:minute:second
            CMD = "sbatch " + sbatch_opts + CMD
        else:
            CMD = CMD + " --no_slurm"

        # Submit the job
        logger.info(f'Job command is: "{CMD}"')
        if notdry(dryrun, logger, '--Dryrun- Would submit command'):
            subprocess.Popen([CMD], shell=True)

    return 0  # a clean, no-issue, exit


def read_batch_spec_file(batch_spec_file):
    batchdict = read_spec(batch_spec_file)

    # Process geographies, and expand any (by matching string pattern) if necessary
    geo_scale = batchdict['geography_scale']
    areas = jeeves.geo.geonames_from_geotypename(geotype=geo_scale)
    strpattern = batchdict['geography_entities']['strmatch']
    GEOAREAS = areas.loc[areas.str.match(strpattern)].tolist()

    # Get study specification file names
    STUDIES = batchdict['study_specs']
    study_pairs = list(itertools.product(GEOAREAS, STUDIES))

    # read other options
    control_options = batchdict['control_options']

    return geo_scale, study_pairs, control_options


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
        opts.batch_spec_filepath = os.path.join(get_run_specs_dir(), 'batch_study_specs', opts.batch_name + '.yaml')

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    sys.exit(main(opts.batch_spec_filepath,
                  dryrun=opts.dryrun, no_slurm=opts.no_slurm))
