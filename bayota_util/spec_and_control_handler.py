#!/usr/bin/env python
import datetime
import itertools
import os
import uuid

import yaml

from bayota_settings.base import get_bayota_version
from bayota_settings.base import get_model_instances_dir, get_control_dir, \
    get_batch_studies_specs_dir, get_experiment_specs_dir, get_model_specs_dir
from bayota_util.str_manip import compact_capitalized_geography_string

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


def read_yaml_to_dict(yaml_file):
    adict = None
    with open(yaml_file, 'r') as stream:
        try:
            adict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    return adict


def read_spec(spec_file_name, spectype):
    if spectype == 'batch':
        spec_dir = get_batch_studies_specs_dir()
    elif spectype == 'model':
        spec_dir = get_model_specs_dir()
    elif spectype == 'experiment':
        spec_dir = get_experiment_specs_dir()
    else:
        raise ValueError(f"Unexpected specification type <{spectype}>")

    spec_path = os.path.join(spec_dir, spec_file_name + '.yaml')
    return read_yaml_to_dict(spec_path)


def read_control(control_file_name):
    control_filepath = os.path.join(get_control_dir(), control_file_name + '.yaml')
    return read_yaml_to_dict(control_filepath)


def overwrite_control(control_file_name, control_dict):
    """ Write (or replace existing) control file with updated dictionary entries """
    control_filepath = os.path.join(get_control_dir(), control_file_name + '.yaml')
    with open(control_filepath, "w") as f:
        yaml.safe_dump(control_dict, f, default_flow_style=False)


def write_control_with_uniqueid(control_dict, control_name_prefix):
    unique_control_name = control_name_prefix + str(uuid.uuid4())
    filepath = os.path.join(get_control_dir(), unique_control_name + '.yaml')
    with open(filepath, "w") as f:
        yaml.safe_dump(control_dict, f, default_flow_style=False)
    return unique_control_name


def parse_batch_spec(batch_spec_name, logger):
    """

    Args:
        batch_spec_name:
        logger:

    Returns:
        geo_scale (str): 'County' or 'lrseg'
        study_paris (list of tuples): tuples are (geographystring, model_form_dictionary)
        control_options (dict):

    """
    jeeves = Jeeves()

    batchdict = read_spec(batch_spec_name, spectype='batch')

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


def read_study_control_file(control_file_name):
    """ The control file is read. """
    control_dict = read_control(control_file_name)

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
    model_dict = read_spec(spec_file_name=model_spec_name, spectype='model')  # Model generation details are saved to control file.
    saved_model_name_for_this_study = 'mdlspec--' + model_spec_name + '--_geo--' + compact_geo_entity_str + '--.pickle'
    control_dict['model'] = {'spec_name': model_spec_name,
                             'objectiveshortname': model_dict['objectiveshortname'],
                             'constraintshortname': model_dict['constraintshortname'],
                             'saved_name_for_this_study': saved_model_name_for_this_study}

    # Experiments
    experiments = studydict['experiments']
    control_dict['experiments'] = experiments.copy()

    # Base Loading Condition
    baseloadingfilename = studydict['base_loading_file_name']
    control_dict['base_loading_file_name'] = baseloadingfilename

    # Run log
    control_dict['code_version']: get_bayota_version()
    control_dict['run_timestamps']['step1_study'] = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')

    # Write (or replace existing) study control file with updated dictionary entries
    overwrite_control(control_file_name=control_file_name, control_dict=control_dict)

    return experiments, baseloadingfilename, control_dict, \
           geo_entity_name, compact_geo_entity_str, model_spec_name, studyshortname, studyid


def read_model_controlfile(control_file_name):
    """ The control file is read. """
    control_dict = read_control(control_file_name)

    geography_scale = control_dict['geography']['scale']
    geography_entity = control_dict['geography']['entity']
    compact_geo_entity_str = control_dict['geography']['shortname']

    model_spec_name = control_dict['model']['spec_name']
    saved_model_name = control_dict['model']['saved_name_for_this_study']
    baseloadingfilename = control_dict['base_loading_file_name']
    savedata2file = control_dict['control_options']['save_model_instance_data_to_file']

    return baseloadingfilename, compact_geo_entity_str, geography_entity, geography_scale, \
           model_spec_name, saved_model_name, savedata2file


def read_expcon_file(control_file_name):
    """ The control file is read. """
    control_dict = read_control(control_file_name)

    studyid = control_dict['study']['id']
    expid = control_dict['experiment']['id']

    expname = control_dict['experiment_name']
    saved_model_name = control_dict['model']['saved_name_for_this_study']
    actionlist = control_dict['experiment']['exp_setup']
    list_of_trialdicts = control_dict['experiment']['trials']
    compact_geo_entity_str = control_dict['geography']['shortname']

    return actionlist, compact_geo_entity_str, control_dict, expid, expname, list_of_trialdicts, \
           saved_model_name, studyid


def read_trialcon_file(control_file_name):
    """ The control file is read. """
    control_dict = read_control(control_file_name)

    studydict = control_dict['study']
    studyid = studydict['id']
    studyshortname = studydict['studyshortname']
    expid = control_dict['experiment']['id']

    model_modification_string = control_dict['trial']['modification'].lstrip('\'').rstrip('\'')

    trialidstr = control_dict['trial']['id']
    trial_name = control_dict['trial']['trial_name']
    saved_model_file = os.path.join(get_model_instances_dir(), control_dict['model']['saved_name_for_this_study'])
    solutions_folder_name = control_dict['trial']['solutions_folder_name']
    compact_geo_entity_str = control_dict['geography']['shortname']

    objective_and_constraint_str = control_dict['model']['objectiveshortname'] + '_' + \
                                   control_dict['model']['constraintshortname']

    # Control Options
    translate_to_cast_format = control_dict['control_options']['translate_solution_table_to_cast_format']
    s3_dict = control_dict['control_options']['move_files_to_s3']
    move_solution_to_s3 = bool(s3_dict['basic_solution'])
    move_CASTformatted_solution_to_s3 = bool(s3_dict['CASTformmated_solution'])
    s3_base_path = s3_dict['base_path_from_modeling-data']

    return compact_geo_entity_str, expid, model_modification_string, move_CASTformatted_solution_to_s3, \
           move_solution_to_s3, objective_and_constraint_str, s3_base_path, saved_model_file, \
           solutions_folder_name, studyid, studyshortname, translate_to_cast_format, trial_name, trialidstr