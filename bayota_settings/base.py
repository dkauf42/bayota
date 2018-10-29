import os
import shutil
import configparser

import logging

user_config_dir = os.path.expanduser("~") + "/.config/" + os.environ['USER']
user_config = user_config_dir + "/bayota_user_config.ini"
bash_config = user_config_dir + "/bayota_bash_config.con"
log_config = user_config_dir + "/bayota_logging_config.cfg"

print('user_config is %s' % user_config)

default_output_dir = os.path.join(os.path.expanduser("~"), 'output')
default_graphics_dir = os.path.join(default_output_dir, 'graphics')
default_logging_dir = os.path.join(default_output_dir, 'logs')

path_to_examples = os.path.dirname(__file__)
example_user_config = os.path.join(path_to_examples, "example_user_config.ini")
example_bash_config = os.path.join(path_to_examples, "example_bash_config.con")
example_log_config = os.path.join(path_to_examples, "example_logging_config.cfg")


def parse_user_config():
    make_user_config()

    config = configparser.ConfigParser()
    config.read(user_config)
    return config


def make_config_file(file_path, example_file):
    if not os.path.isfile(file_path):
        os.makedirs(user_config_dir, exist_ok=True)
        shutil.copyfile(example_file, file_path)


def make_user_config():
    make_config_file(file_path=bash_config, example_file=example_bash_config)


def make_bash_config():
    make_config_file(file_path=user_config, example_file=example_user_config)


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

    with open("example_user_config.ini", 'w') as f:
        config.write(f)
