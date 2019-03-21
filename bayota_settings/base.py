"""
This script sets up a user's workspace directory during install,
 and also provides methods for grabbing required directories during a run.
================================================================================
"""
import os
import shutil
import configparser
import pkg_resources

import logging
import logging.config


def get_bayota_version(verbose=False):
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


def get_example_config_path():
    example_config_path = pkg_resources.resource_filename('bayota_settings', 'install_config.ini')
    return example_config_path


# Example Config Files
path_to_examples = os.path.dirname(__file__)
example_user_config = os.path.join(path_to_examples, "install_config.ini")
example_bash_config = os.path.join(path_to_examples, "example_bash_config.con")
example_log_config = os.path.join(path_to_examples, "example_logging_config.cfg")


class BayotaConfigured:
    def __init__(self, verbose=False):

        self.version = get_bayota_version()

        # The version number is updated in the config file.
        parser = configparser.ConfigParser(os.environ,
                                           interpolation=configparser.ExtendedInterpolation(),
                                           comment_prefixes=('#', ';'))
        parser.read(get_example_config_path())
        parser.set("version", "version", str(self.version))

        ws_dir = parser['top_paths']['workspace_top']
        if verbose:
            print('bayota_settings.base(): ws_dir = %s' % ws_dir)
        os.makedirs(ws_dir, exist_ok=True)

        self.config_dir = parser['workspace_directories']['config']
        self.user_config = parser['other_config']['userconfigcopy']
        self.bash_config = parser['other_config']['bashconfig']
        self.log_config = parser['other_config']['logconfig']

        self.default_output_dir = parser['output_directories']['general']
        self.default_graphics_dir = parser['output_directories']['graphics']
        self.default_logging_dir = parser['output_directories']['logs']

    def make_config_file(self, file_path, example_file):
        created = False
        if not os.path.isfile(file_path):
            os.makedirs(self.config_dir, exist_ok=True)
            shutil.copyfile(example_file, file_path)
            created = True
        return created

    def parse_user_config(self):
        self.make_user_config()

        config = configparser.ConfigParser(os.environ, interpolation=configparser.ExtendedInterpolation())
        config.read(self.user_config)

        return config

    def make_user_config(self):
        created = self.make_config_file(file_path=self.user_config,
                                        example_file=example_user_config)
        if created:
            # Ensure version is up-to-date
            config = configparser.ConfigParser()
            config.read(self.user_config)

            config.set("version", "version", str(self.version))

            with open(self.user_config, 'w') as newini:
                config.write(newini)

    def make_bash_config(self):
        self.make_config_file(file_path=self.bash_config,
                              example_file=example_bash_config)

    def make_log_config(self):
        self.make_config_file(file_path=self.log_config,
                              example_file=example_log_config)

    def write_example_config(self):
        config = configparser.ConfigParser()

        config.add_section('output_directories')
        config['output_directories']['general'] = self.default_output_dir
        config['output_directories']['graphics'] = self.default_graphics_dir
        config['output_directories']['logs'] = self.default_logging_dir

        # config.add_section('settings')
        # config['settings']['logging'] = default_logging_dir

        with open("install_config.ini", 'w') as f:
            config.write(f)


class MyLogFormatter(logging.Formatter):
    """Note: this class is used in the log configuration file (typically stored in ~/.config/$USER/)
    """
    def format(self, record):
        location = '%s.%s:%s' % (record.name, record.funcName, record.lineno)
        msg = '%s %-100s %-8s %s' % (self.formatTime(record), location, record.levelname, record.msg)
        record.msg = msg
        return super(MyLogFormatter, self).format(record)


bayota_configured = BayotaConfigured()
logdir = bayota_configured.parse_user_config()['output_directories']['logs']
os.makedirs(logdir, exist_ok=True)
logfilename = os.path.join(logdir, 'efficiencysubproblem_debug.log')


def set_up_logger():
    bayota_configured.make_log_config()

    logging.config.fileConfig(bayota_configured.log_config,
                              defaults={'logfilename': logfilename},
                              disable_existing_loggers=False)


def get_source_csvs_dir():
    datadir_top_level = bayota_configured.parse_user_config()['data_directories']['sourcecsvs']
    if not os.path.isdir(datadir_top_level):
        raise ValueError('Source CSVs directory (%s) specified in config does not exist!' % datadir_top_level)

    return datadir_top_level


def get_raw_data_dir():
    rawdatadir = bayota_configured.parse_user_config()['data_directories']['rawdata']
    if not os.path.isdir(rawdatadir):
        raise ValueError('Raw data directory (%s) specified in config does not exist!' % rawdatadir)

    return rawdatadir


def _make_or_get_user_dir(section, key):
    dir = bayota_configured.parse_user_config()[section][key]
    os.makedirs(dir, exist_ok=True)
    return dir


def get_output_dir():
    return _make_or_get_user_dir('output_directories', 'general')
def get_scripts_dir():
    return _make_or_get_user_dir('top_paths', 'scripts')
def get_control_dir():
    return _make_or_get_user_dir('workspace_directories', 'control')
def get_spec_files_dir():
    return _make_or_get_user_dir('top_paths', 'spec_files_top')
def get_single_study_specs_dir():
    return _make_or_get_user_dir('specification_file_directories', 'single_studies')
def get_batch_studies_specs_dir():
    return _make_or_get_user_dir('specification_file_directories', 'batch_studies')
def get_model_specs_dir():
    return _make_or_get_user_dir('specification_file_directories', 'models')
def get_experiment_specs_dir():
    return _make_or_get_user_dir('specification_file_directories', 'experiments')
def get_graphics_dir():
    return _make_or_get_user_dir('output_directories', 'graphics')
def get_source_pickles_dir():
    return _make_or_get_user_dir('temp_directories', 'source_pickles')
def get_model_instances_dir():
    return _make_or_get_user_dir('temp_directories', 'model_instances')
