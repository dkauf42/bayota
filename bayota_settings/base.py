"""
This script sets up a user's workspace directory during install,
 and also provides methods for grabbing required directories during a run.
================================================================================
"""
import os
import shutil
import configparser
import pkg_resources


def get_bayota_version(verbose=False) -> str:
    try:
        version = pkg_resources.require("bayota")[0].version
    except pkg_resources.DistributionNotFound:
        print('installed "bayota" pkg-resources not found. Running from source.')
        try:
            with open('VERSION', 'r') as f:
                for line in f:
                    version = line
                    break
        except FileNotFoundError:
            print("bayota_settings.base.get_bayota_version(): unable to open VERSION file")
            raise
    if verbose:
        print('bayota_settings.base.get_bayota_version(): version = %s' % version)
    return version


# The version number is retrieved.
version = get_bayota_version()

# Example configuration files are retrieved from this directory.
example_user_config = pkg_resources.resource_filename('bayota_settings', 'install_config.ini')
example_bash_config = pkg_resources.resource_filename('bayota_settings', 'example_bash_config.con')
example_log_config = pkg_resources.resource_filename('bayota_settings', 'example_logging_config.yaml')

# A configuration object (for holding paths and settings) is generated from the example file.
config_obj = configparser.ConfigParser(os.environ,
                                       interpolation=configparser.ExtendedInterpolation(),
                                       comment_prefixes=('#', ';'))
config_obj.read(example_user_config)
# The code version number is saved to the configuration object (note: other user config paths may depend on it).
config_obj.set("version", "version", str(version))

# Directories are retrieved from the example configuration.
config_dir = config_obj['workspace_directories']['config']

default_output_dir = config_obj['output_directories']['general']
default_graphics_dir = config_obj['output_directories']['graphics']
default_logging_dir = config_obj['output_directories']['logs']

# Paths for configuration files are retrieved.
user_config = config_obj['other_config']['userconfigcopy']
bash_config = config_obj['other_config']['bashconfig']
log_config = config_obj['other_config']['logconfig']

''' "Private" helper functions '''


def _create_file_in_config_dir_if_doesnt_exist(file_path, example_file) -> bool:
    created = False
    if not os.path.isfile(file_path):
        os.makedirs(config_dir, exist_ok=True)
        shutil.copyfile(example_file, file_path)
        created = True
    return created


def _ensure_user_config_file_exists_with_current_version_number():
    created = _create_file_in_config_dir_if_doesnt_exist(file_path=user_config, example_file=example_user_config)
    if created:
        # Ensure version is up-to-date
        config = configparser.ConfigParser()
        config.read(user_config)

        config.set("version", "version", str(version))

        with open(user_config, 'w') as newini:
            config.write(newini)


def _parse_user_config() -> configparser.ConfigParser:
    _ensure_user_config_file_exists_with_current_version_number()

    config = configparser.ConfigParser(os.environ, interpolation=configparser.ExtendedInterpolation())
    config.read(user_config)

    return config


def _make_or_get_user_dir(section, key) -> str:
    dir = _parse_user_config()[section][key]
    os.makedirs(dir, exist_ok=True)
    return dir


''' "Public" set-up and getter functions '''


def create_workspace_directory_and_set_up_user_config_files(verbose=True):
    ws_dir = config_obj['top_paths']['workspace_top']
    if verbose:
        print('bayota_settings.base(): ws_dir = %s' % ws_dir)
    os.makedirs(ws_dir, exist_ok=True)

    _ensure_user_config_file_exists_with_current_version_number()
    _create_file_in_config_dir_if_doesnt_exist(file_path=bash_config, example_file=example_bash_config)
    _create_file_in_config_dir_if_doesnt_exist(file_path=log_config, example_file=example_log_config)


def get_source_csvs_dir() -> str:
    datadir_top_level = _parse_user_config()['data_directories']['sourcecsvs']
    if not os.path.isdir(datadir_top_level):
        raise ValueError('Source CSVs directory (%s) specified in config does not exist!' % datadir_top_level)

    return datadir_top_level


def get_raw_data_dir() -> str:
    rawdatadir = _parse_user_config()['data_directories']['rawdata']
    if not os.path.isdir(rawdatadir):
        raise ValueError('Raw data directory (%s) specified in config does not exist!' % rawdatadir)

    return rawdatadir


def get_output_dir() -> str:
    return _make_or_get_user_dir('output_directories', 'general')
def get_scripts_dir() -> str:
    return _make_or_get_user_dir('top_paths', 'scripts')
def get_control_dir() -> str:
    return _make_or_get_user_dir('workspace_directories', 'control')
def get_logging_dir() -> str:
    return _make_or_get_user_dir('output_directories', 'logs')
def get_spec_files_dir() -> str:
    return _make_or_get_user_dir('top_paths', 'spec_files_top')
def get_single_study_specs_dir() -> str:
    return _make_or_get_user_dir('specification_file_directories', 'single_studies')
def get_batch_studies_specs_dir() -> str:
    return _make_or_get_user_dir('specification_file_directories', 'batch_studies')
def get_model_specs_dir() -> str:
    return _make_or_get_user_dir('specification_file_directories', 'models')
def get_experiment_specs_dir() -> str:
    return _make_or_get_user_dir('specification_file_directories', 'experiments')
def get_graphics_dir() -> str:
    return _make_or_get_user_dir('output_directories', 'graphics')
def get_source_pickles_dir() -> str:
    return _make_or_get_user_dir('temp_directories', 'source_pickles')
def get_model_instances_dir() -> str:
    return _make_or_get_user_dir('temp_directories', 'model_instances')
