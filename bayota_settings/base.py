import os
import shutil
import configparser

import logging

user_config_dir = os.path.expanduser("~") + "/.config/" + os.environ['USER']
user_config = user_config_dir + "/bayota_user_config.ini"
bash_config = user_config_dir + "/bayota_bash_config.ini"
log_config = user_config_dir + "/bayota_logging_config.cfg"

print('user_config is %s' % user_config)

default_output_dir = os.path.join(os.path.expanduser("~"), 'output')
default_graphics_dir = os.path.join(default_output_dir, 'graphics')
default_logging_dir = os.path.join(default_output_dir, 'logs')


def parse_config():
    make_user_config()

    config = configparser.ConfigParser()
    config.read(user_config)
    return config


def make_user_config():
    if not os.path.isfile(user_config):
        os.makedirs(user_config_dir, exist_ok=True)
        shutil.copyfile("example_config.ini", user_config)

def make_bash_config():
    if not os.path.isfile(bash_config):
        os.makedirs(user_config_dir, exist_ok=True)
        shutil.copyfile("example_bash_config.ini", bash_config)

def make_log_config():
    if not os.path.isfile(log_config):
        os.makedirs(user_config_dir, exist_ok=True)
        shutil.copyfile("example_logging_config.ini", log_config)


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

    with open("example_config.ini", 'w') as f:
        config.write(f)
