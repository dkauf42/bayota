import os
import shutil
import configparser

user_config_dir = os.path.expanduser("~") + "/.config/" + os.environ['USER']
user_config = user_config_dir + "/bayota_user_config.ini"
user_log_config = user_config_dir + "/bayota_logging_config.cfg"

print('user_config is %s' % user_config)

default_output_dir = os.path.join(os.path.expanduser("~"), 'output')
default_graphics_dir = os.path.join(default_output_dir, 'graphics')
default_logging_dir = os.path.join(default_output_dir, 'logs')


def parse_config():
    if not os.path.isfile(user_config):
        os.makedirs(user_config_dir, exist_ok=True)
        shutil.copyfile("example_config.ini", user_config)

    config = configparser.ConfigParser()
    config.read(user_config)
    return config


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
