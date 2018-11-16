import os
import shutil
import configparser
import pkg_resources

import logging

install_config_path = os.path.join('bayota_settings', 'install_config.ini')

install_config = configparser.ConfigParser(os.environ, interpolation=configparser.ExtendedInterpolation())
install_config.read(install_config_path)

# Get (or make if doesn't exist) Workspace Directory
ws_dir = install_config['top_paths']['workspace_top']
print('bayota_settings.base(): ws_dir = %s' % ws_dir)
os.makedirs(ws_dir, exist_ok=True)

repo_dir = install_config['top_paths']['repo_top']


def get_bayota_version():
    try:
        version = pkg_resources.require("bayota")[0].version
        print('bayota_settings.base(): version = %s' % version)
    except pkg_resources.DistributionNotFound:
        print('installed "bayota" pkg-resources not found. Running from source.')
        try:
            with open(os.path.join(repo_dir, 'VERSION'), 'r') as f:
                for line in f:
                    version = line
                    break
        except:
            print("bayota_settings.base.get_bayota_version(): unable to open VERSION file")
            version = '0.0.-'
    return version


# The version number is updated in the config file.
version = get_bayota_version()
install_config.set("version", "version", str(version))

config_dir = install_config['workspace_directories']['config']
user_config = install_config['other_config']['userconfigcopy']
bash_config = install_config['other_config']['bashconfig']
log_config = install_config['other_config']['logconfig']

default_output_dir = install_config['output_directories']['general']
default_graphics_dir = install_config['output_directories']['graphics']
default_logging_dir = install_config['output_directories']['logs']

path_to_examples = os.path.dirname(__file__)
example_user_config = os.path.join(path_to_examples, "install_config.ini")
example_bash_config = os.path.join(path_to_examples, "example_bash_config.con")
example_log_config = os.path.join(path_to_examples, "example_logging_config.cfg")


def make_config_file(file_path, example_file):
    created = False
    if not os.path.isfile(file_path):
        os.makedirs(config_dir, exist_ok=True)
        shutil.copyfile(example_file, file_path)
        created = True
    return created


def parse_user_config():
    make_user_config()

    config = configparser.ConfigParser(os.environ, interpolation=configparser.ExtendedInterpolation())
    config.read(user_config)

    return config


def make_user_config():
    created = make_config_file(file_path=user_config, example_file=example_user_config)
    if created:
        # Ensure version is up-to-date
        config = configparser.ConfigParser()
        config.read(user_config)

        config.set("version", "version", str(version))

        with open(user_config, 'w') as newini:
            config.write(newini)


def make_bash_config():
    make_config_file(file_path=bash_config, example_file=example_bash_config)


def make_log_config():
    make_config_file(file_path=log_config, example_file=example_log_config)


class MyLogFormatter(logging.Formatter):
    """Note: this class is used in the log configuration file (typically stored in ~/.config/$USER/)
    """
    def format(self, record):
        location = '%s.%s:%s' % (record.name, record.funcName, record.lineno)
        msg = '%s %-100s %-8s %s' % (self.formatTime(record), location, record.levelname, record.msg)
        record.msg = msg
        return super(MyLogFormatter, self).format(record)


def write_example_config():
    config = configparser.ConfigParser()

    config.add_section('output_directories')
    config['output_directories']['general'] = default_output_dir
    config['output_directories']['graphics'] = default_graphics_dir
    config['output_directories']['logs'] = default_logging_dir

    # config.add_section('settings')
    # config['settings']['logging'] = default_logging_dir

    with open("install_config.ini", 'w') as f:
        config.write(f)
