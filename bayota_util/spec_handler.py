#!/usr/bin/env python
import datetime
import itertools
import os

import yaml
from argparse import ArgumentParser

from bayota_settings.base import get_model_specs_dir, get_model_instances_dir
from bayota_util.str_manip import compact_capitalized_geography_string
from bayota_settings.base import get_spec_files_dir

geo_spec_file = os.path.join(get_spec_files_dir(), 'geography_specs.yaml')

from castjeeves.jeeves import Jeeves


def notdry(dryrun, logger=None, descr=''):
    if not dryrun:
        return True
    else:
        if not logger:
            print(descr)
        else:
            logger.info(descr)
        return False


def read_spec(spec_file):
    adict = None
    with open(spec_file, 'r') as stream:
        try:
            adict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    return adict


def parse_cli_arguments():
    """ Input arguments are parsed. """
    parser = ArgumentParser()
    one_or_the_other = parser.add_mutually_exclusive_group(required=True)
    one_or_the_other.add_argument("-s", "--study_spec", dest="study_spec_file", default=None,
                                  help="read_spec in a study specification file")
    one_or_the_other.add_argument("-e", "--experiment_spec", dest="experiment_spec_file", default=None,
                                  help="read_spec in an experiment specification file")
    opts = parser.parse_args()

    if not opts.experiment_spec_file:  # study spec was given
        opts.specfile = opts.study_spec_file
    else:  # experiment spec was given
        opts.specfile = opts.experiment_spec_file

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    adict = read_spec(opts.specfile)

    print(adict)


def read_batch_spec_file(batch_spec_file, logger):
    """

    Args:
        batch_spec_file:
        logger:

    Returns:
        geo_scale (str): 'County' or 'lrseg'
        study_paris (list of tuples): tuples are (geographystring, model_form_dictionary)
        control_options (dict):

    """
    jeeves = Jeeves()

    batchdict = read_spec(batch_spec_file)

    # Process geographies, and expand any (by matching string pattern) if necessary
    geo_scale = batchdict['geography_scale']
    areas = jeeves.geo.geonames_from_geotypename(geotype=geo_scale)
    strpattern = batchdict['geography_entities']['strmatch']

    if type(strpattern) is list:
        GEOAREAS = []
        for sp in strpattern:
            for item in areas.loc[areas.str.lower().str.match(sp.lower())].tolist():
                GEOAREAS.append(item)
    else:
        GEOAREAS = areas.loc[areas.str.lower().str.match(strpattern.lower())].tolist()

    # Get study specification file names
    STUDIES = batchdict['study_specs']
    study_pairs = list(itertools.product(GEOAREAS, STUDIES))

    # read other options
    control_options = batchdict['control_options']

    logger.info('%d %s to be conducted: %s' %
                (len(study_pairs),
                 'study' if len(study_pairs) == 1 else 'studies',
                 study_pairs))

    return geo_scale, study_pairs, control_options


def read_study_control_file(control_file, version):
    if not control_file:
        raise ValueError('A control file must be specified.')

    control_dict = read_spec(control_file)

    studydict = control_dict['study']
    studyshortname = studydict['studyshortname']
    studyid = studydict['id']

    # Geography
    geodict = control_dict['geography']
    geo_entity_name = geodict['entity']
    compact_geo_entity_str = compact_capitalized_geography_string(geo_entity_name)
    geodict['shortname'] = compact_geo_entity_str
    control_dict['geography'] = geodict

    # Model Specification
    model_spec_name = studydict['model_spec']
    model_spec_file = model_spec_name
    model_dict = read_spec(os.path.join(get_model_specs_dir(), model_spec_name + '.yaml'))  # Model generation details are saved to control file.
    saved_model_name_for_this_study = 'mdlspec--' + model_spec_name + '--_geo--' + compact_geo_entity_str + '--.pickle'
    control_dict['model'] = {'spec_file': model_spec_file,
                             'objectiveshortname': model_dict['objectiveshortname'],
                             'constraintshortname': model_dict['constraintshortname'],
                             'saved_file_for_this_study': saved_model_name_for_this_study}

    # Experiments
    experiments = studydict['experiments']
    control_dict['experiments'] = experiments.copy()

    # Base Loading Condition
    baseloadingfilename = studydict['base_loading_file_name']
    control_dict['base_loading_file_name'] = baseloadingfilename

    # Run log
    control_dict['code_version']: version
    control_dict['run_timestamps']['step1_study'] = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')

    # Write (or replace existing) study control file with updated dictionary entries
    with open(control_file, "w") as f:
        yaml.safe_dump(control_dict, f, default_flow_style=False)

    return experiments, baseloadingfilename, control_dict, \
           geo_entity_name, compact_geo_entity_str, model_spec_name, studyshortname, studyid


def read_model_controlfile(baseloadingfilename, control_file, geography_name, model_spec_file, saved_model_file):
    # The control file is read.
    if not not control_file:
        control_dict = read_spec(control_file)

        geography_scale = control_dict['geography']['scale']
        geography_entity = control_dict['geography']['entity']
        compact_geo_entity_str = control_dict['geography']['shortname']

        model_spec_file = control_dict['model']['spec_file']
        saved_model_file = control_dict['model']['saved_file_for_this_study']
        baseloadingfilename = control_dict['base_loading_file_name']
        savedata2file = control_dict['control_options']['save_model_instance_data_to_file']
    else:
        geodict = read_spec(geo_spec_file)[geography_name]
        geography_scale = geodict['scale']
        geography_entity = geodict['entities']
        compact_geo_entity_str = compact_capitalized_geography_string(geography_entity)

        savedata2file = False
    return baseloadingfilename, compact_geo_entity_str, geography_entity, geography_scale, model_spec_file, saved_model_file, savedata2file


def read_expcon_file(control_file, experiment_spec_file=None, saved_model_file=None):
    # The control file is read.
    if not not control_file:
        control_dict = read_spec(control_file)

        studyid = control_dict['study']['id']
        expid = control_dict['experiment']['id']

        expname = os.path.splitext(os.path.basename(control_dict['experiment_file']))[0]
        saved_model_file = control_dict['model']['saved_file_for_this_study']
        actionlist = control_dict['experiment']['exp_setup']
        list_of_trialdicts = control_dict['experiment']['trials']
        compact_geo_entity_str = control_dict['geography']['shortname']
    else:
        control_dict = dict()
        studyid = '0000'
        expid = '0000'
        expname = os.path.splitext(os.path.basename(experiment_spec_file))[0]
        actionlist = read_spec(experiment_spec_file)['exp_setup']
        list_of_trialdicts = read_spec(experiment_spec_file)['trials']
        compact_geo_entity_str = ''
    return actionlist, compact_geo_entity_str, control_dict, expid, expname, list_of_trialdicts, saved_model_file, studyid